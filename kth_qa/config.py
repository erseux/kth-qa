import logging
logger = logging.getLogger()
import openai
from pydantic import BaseSettings

from kth_qa.magic.vectordb import VectorIndex

from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain

from magic.prompts import PROMPT, EXAMPLE_PROMPT
import json

class Settings(BaseSettings):
    OPENAI_API_KEY: str = 'OPENAI_API_KEY'
    OPENAI_CHAT_MODEL: str = 'gpt-3.5-turbo'
    class Config:
        env_file = 'C:\\Users\\46705\\Documents\\Search_engines\\project_work\\kth-qa\\kth_qa\\.env'

def set_openai_key(key):
    """Sets OpenAI key."""
    openai.api_key = key

class Config:
    settings: Settings
    store: VectorIndex
    chain: RetrievalQAWithSourcesChain
    courses: list

    def __init__(self, debug=False):
        self.debug = debug
        self.settings = Settings()

        self._load_courses()

        # OPENAI
        set_openai_key(self.settings.OPENAI_API_KEY)

        # Langchain
        self.store: VectorIndex = VectorIndex()

         # CHAIN
        doc_chain = self._load_doc_chain()
        self.chain = RetrievalQAWithSourcesChain(combine_documents_chain=doc_chain, 
                                            retriever=self.store.as_retriever(search_kwargs=dict(k=5)))
        
    def _load_doc_chain(self):
        doc_chain = load_qa_with_sources_chain(
            ChatOpenAI(temperature=0, max_tokens=100, model=self.settings.OPENAI_CHAT_MODEL, request_timeout=120),
            chain_type="stuff",
            document_variable_name="context",
            prompt=PROMPT,
            document_prompt=EXAMPLE_PROMPT,
        )
        return doc_chain
    
    def _load_courses(self):
        with open('courses.json') as json_file:
            data = json.load(json_file)
            self.courses = data['courses']

    def course_exists(self, course: str):
        course = course.upper()
        exists = course in self.courses
        if exists:
            logger.info(f'Course {course} exists')
            return True
        else:
            logger.info(f'Course {course} does not exist')
            return False