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
    with get_openai_callback() as cb:
        # make sure pwd is kth_qa
        pwd = os.getcwd()
        if pwd.split('/')[-1] != 'kth_qa':
            logger.error(f"pwd is not kth_qa, but {pwd}. Please run from kth_qa directory.")
            return
        
        text_splitter = NLTKTextSplitter.from_tiktoken_encoder(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=100,
        )
            
        # file_folder_name = f'files/{DEFAULT_LANGUAGE}'
        file_folder_name = f'files/all'
        file_folder = os.listdir(file_folder_name)
        all_langdocs = []
        for file in file_folder:
            raw_docs = []
            try: 
                with open(f'{file_folder_name}/{file}', 'r') as f:
                    if file == '.DS_Store':
                        continue
                    text = f.read()
                    filename = file.split('.')[0]
                    course_code, language = filename.split('?l=')
                    doc = Document(page_content=text, metadata={"course": course_code})
                    raw_docs.append(doc)
                    logger.debug(f"loaded file {file}")

                    langdocs = text_splitter.split_documents(raw_docs)
                    logger.debug(f"split documents into {len(langdocs)} chunks")
                    all_langdocs.extend(langdocs)
            except:
                logger.error(f"failed to load file {file}")

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