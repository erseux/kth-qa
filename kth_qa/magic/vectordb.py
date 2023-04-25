import logging
logger = logging.getLogger()
import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from ingest import PERSIST_DIR

embedding = OpenAIEmbeddings()
class VectorIndex(Chroma):
    def __init__(self):
        if len(os.listdir(PERSIST_DIR)) < 2: # check if there are files in the directory
            logger.error(f"VectorIndex: No files in {PERSIST_DIR}, have you run ingest.py?")
        super().__init__(persist_directory=PERSIST_DIR, embedding_function=embedding)