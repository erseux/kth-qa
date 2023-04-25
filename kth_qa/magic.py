import logging
logger = logging.getLogger()
import os
from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class VectorIndex:
    def __init__(self):
        self.index = None
        self.add_documents()
        
    def add_documents(self):
        folder = os.listdir(f'files')
        loaders = []
        for file in folder:
            loader = TextLoader(f'files/{file}', encoding="utf-8")
            loaders.append(loader)
            logger.info(f"loaded file {file} to index")
        self.index = VectorstoreIndexCreator().from_loaders(loaders)

    def query(self, question):
        if not self.index:
            logger.debug("index not created yet")
            return None
        answer = self.index.query(question)
        logger.info(f"got answer: {answer}")
        return answer