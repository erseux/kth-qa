import logging

from utils import get_courses
logger = logging.getLogger()

import os
from langchain.docstore.document import Document
from langchain.text_splitter import NLTKTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

PERSIST_DIR = 'db'
FILE_DIR = 'files'
KURS_URL = "https://www.kth.se/student/kurser/kurs/{course_code}?l={language}"
DEFAULT_LANGUAGE = "en"

def ingest():
    # make sure pwd is kth_qa
    pwd = os.getcwd()
    if pwd.split('/')[-1] != 'kth_qa':
        logger.error(f"ingest.py: pwd is not kth_qa, but {pwd}. Please run from kth_qa directory.")
        return
    
    embedding = OpenAIEmbeddings()
    courses = get_courses()
        
    file_folder_name = f'files/{DEFAULT_LANGUAGE}'
    file_folder = os.listdir(file_folder_name)
    raw_docs = []
    course_codes = []
    for file in file_folder:
        with open(f'{file_folder_name}/{file}', 'r') as f:
            text = f.read()
            filename = file.split('.')[0]
            course_code, language = filename.split('?l=')
            course_codes.append(course_code)
            # url = KURS_URL.format(course_code=course_code, language=language)
            doc = Document(page_content=text, metadata={"source": course_code})
            raw_docs.append(doc)
            logger.info(f"loaded file {file}")

    text_splitter = NLTKTextSplitter.from_tiktoken_encoder(
        chunk_size=500,
        chunk_overlap=100,
    )
    langdocs = text_splitter.split_documents(raw_docs)
    # add course title to page content in each document
    for langdoc, course_code in zip(langdocs, course_codes):
        course_title = courses.get(course_code).get(DEFAULT_LANGUAGE) 
        course_title = course_title.rsplit(',', 1)[0]
        langdoc.page_content = course_title + '\n' + doc.page_content
    logger.info(f"split documents into {len(langdocs)} chunks")

    vectordb = Chroma.from_documents(documents=langdocs, embedding=embedding, persist_directory=PERSIST_DIR)
    logger.info(f"created vector index")
    vectordb.persist()
    logger.info(f"persisted vector index")
    vectordb = None
    logger.info(f"Done!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(logging.INFO)
    ingest()