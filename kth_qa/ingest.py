import logging

from utils import get_courses
logger = logging.getLogger()

import os
from langchain.docstore.document import Document
from langchain.text_splitter import NLTKTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.callbacks import get_openai_callback

PERSIST_DIR = 'db'
FILE_DIR = 'files'
KURS_URL = "https://www.kth.se/student/kurser/kurs/{course_code}?l={language}"
DEFAULT_LANGUAGE = "en"

def ingest():
    # make sure pwd is kth_qa
    with get_openai_callback() as cb:
        pwd = os.getcwd()
        if pwd.split('/')[-1] != 'kth_qa':
            logger.error(f"pwd is not kth_qa, but {pwd}. Please run from kth_qa directory.")
            return
        
        embedding = OpenAIEmbeddings(chunk_size=1000)

        text_splitter = NLTKTextSplitter.from_tiktoken_encoder(
            chunk_size=1000,
            chunk_overlap=100,
        )
            
        file_folder_name = f'files/{DEFAULT_LANGUAGE}'
        file_folder = os.listdir(file_folder_name)
        all_langdocs = []
        for file in file_folder:
            raw_docs = []
            with open(f'{file_folder_name}/{file}', 'r') as f:
                text = f.read()
                filename = file.split('.')[0]
                course_code, language = filename.split('?l=')
                doc = Document(page_content=text, metadata={"source": course_code})
                raw_docs.append(doc)
                logger.debug(f"loaded file {file}")

                langdocs = text_splitter.split_documents(raw_docs)
                logger.debug(f"split documents into {len(langdocs)} chunks")
                all_langdocs.extend(langdocs)

        # add course title to page content in each document
        logger.info(f"split all documents into {len(all_langdocs)} chunks")

        logger.info(f"creating vector index in Chroma...")
        vectordb = Chroma.from_documents(documents=all_langdocs, 
                                         embedding=embedding, 
                                         persist_directory=PERSIST_DIR)
        logger.info(f"created vector index")
        vectordb.persist()
        logger.info(f"persisted vector index")
        vectordb = None
        logger.info(f"Done!")

        logger.info(f"Total cost of openai api calls: {cb.total_cost}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)
    ingest()