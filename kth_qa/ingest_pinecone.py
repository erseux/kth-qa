import logging
logger = logging.getLogger()

import os
from langchain.docstore.document import Document
from langchain.text_splitter import NLTKTextSplitter
from langchain.callbacks import get_openai_callback

from kth_qa.config import State

FILE_DIR = 'files'
KURS_URL = "https://www.kth.se/student/kurser/kurs/{course_code}?l={language}"
DEFAULT_LANGUAGE = "en"
CHUNK_SIZE = 1000

def ingest(state: State):
    # make sure pwd is kth_qa
    with get_openai_callback() as cb:
        pwd = os.getcwd()
        if pwd.split('/')[-1] != 'kth_qa':
            logger.error(f"pwd is not kth_qa, but {pwd}. Please run from kth_qa directory.")
            return
        
        text_splitter = NLTKTextSplitter.from_tiktoken_encoder(
            chunk_size=CHUNK_SIZE,
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
                doc = Document(page_content=text, metadata={"course": course_code})
                raw_docs.append(doc)
                logger.debug(f"loaded file {file}")

                langdocs = text_splitter.split_documents(raw_docs)
                logger.debug(f"split documents into {len(langdocs)} chunks")
                all_langdocs.extend(langdocs)

        # add course title to page content in each document
        logger.info(f"split all documents into {len(all_langdocs)} chunks")

        logger.info(f"Adding documents to pinecone...")
        state.store.add_documents(all_langdocs)
        logger.info(f"...done!")

        logger.info(f"Total cost of openai api calls: {cb.total_cost}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)

    state = State()
    ingest(state)