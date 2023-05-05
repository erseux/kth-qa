from ingest import PERSIST_DIR
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
import os
import logging
logger = logging.getLogger()

embedding = OpenAIEmbeddings()


class LocalVectorIndex(Chroma):
    def __init__(self):
        if len(os.listdir(PERSIST_DIR)) < 2:  # check if there are files in the directory
            logger.error(
                f"VectorIndex: No files in {PERSIST_DIR}, have you run ingest.py?")
        super().__init__(persist_directory=PERSIST_DIR, embedding_function=embedding)
