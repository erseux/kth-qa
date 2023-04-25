import logging
logger = logging.getLogger()

import os
from langchain.docstore.document import Document
from langchain.text_splitter import NLTKTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma

PERSIST_DIR = 'db'
FILE_DIR = 'files'
KURS_URL = "https://www.kth.se/student/kurser/kurs/{course_name}?l=en"

def ingest():
    embedding = OpenAIEmbeddings()

    file_folder = os.listdir(f'files')
    raw_docs = []
    for file in file_folder:
        with open(f'files/{file}', 'r') as f:
            text = f.read()
            filename = file.split('.')[0]
            url = KURS_URL.format(course_name=filename)
            doc = Document(page_content=text, metadata={"source": filename})
            raw_docs.append(doc)
            logger.info(f"loaded file {file} to index")

    text_splitter = NLTKTextSplitter.from_tiktoken_encoder(
        chunk_size=400,
        chunk_overlap=100,
    )
    langdocs = text_splitter.split_documents(raw_docs)
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