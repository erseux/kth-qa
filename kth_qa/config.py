from magic.vectordb import LocalVectorIndex
from magic.prompts import PROMPT, EXAMPLE_PROMPT
from magic.self_query_retriever import SelfQueryRetriever
from kth_qa.utils import get_courses
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains import SequentialChain
from langchain.llms import OpenAI
from langchain.chains import LLMCheckerChain
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import openai
import pinecone
from pydantic import BaseSettings
from typing import Literal, Union
import logging
logger = logging.getLogger()


class Settings(BaseSettings):
    OPENAI_API_KEY: str = 'OPENAI_API_KEY'
    OPENAI_CHAT_MODEL: str = 'gpt-3.5-turbo'
    PINECONE_API_KEY: str = 'PINECONE_API_KEY'
    PINECONE_INDEX_NAME: str = 'kth-qa'
    PINECONE_ENV: str = 'us-west1-gcp-free'

    class Config:
        env_file = '.env'


def set_openai_key(key):
    """Sets OpenAI key."""
    openai.api_key = key


class State:
    settings: Settings
    store: Union[Pinecone, LocalVectorIndex]
    chain: RetrievalQAWithSourcesChain
    courses: list

    def __init__(self, vectorstore: Literal['local', 'pinecone'] = 'pinecone', self_query=True, sequential_chain: bool = False):
        if vectorstore == 'local':
            self.self_query = False  # self_query is not supported for local vectorstore
        else:
            self.self_query = self_query

        self.settings = Settings()

        self.courses = get_courses()

        # OPENAI
        set_openai_key(self.settings.OPENAI_API_KEY)

        # VECTORSTORE
        if vectorstore == 'local':
            self.store: LocalVectorIndex = LocalVectorIndex()
        elif vectorstore == 'pinecone':
            embeddings = OpenAIEmbeddings()
            pinecone.init(api_key=self.settings.PINECONE_API_KEY,
                          environment=self.settings.PINECONE_ENV)
            self.store: Pinecone = Pinecone.from_existing_index(
                self.settings.PINECONE_INDEX_NAME, embeddings, "text")
            logger.info(f"Pinecone store initialized")

        # CHAINS
        doc_chain = self._load_doc_chain()
        qa_chain = self._load_qa_chain(doc_chain)

        if sequential_chain:  # SEQ CHAIN with QA and CHECKER
            checker_chain = self._load_checker_chain()
            self.chain = self._load_seq_chain([self.chain, checker_chain])
        else:         # JUST QA
            self.chain = qa_chain

    def _load_seq_chain(self, chains):
        sequential_chain = SequentialChain(
            chains=chains,
            input_variables=["question"],
            output_variables=["answer"],
            verbose=True)
        return sequential_chain

    def _load_checker_chain(self):
        llm = OpenAI(temperature=0)
        checker_chain = LLMCheckerChain(
            llm=llm, verbose=True, input_key="answer", output_key="result")
        return checker_chain

    def _load_doc_chain(self):
        doc_chain = load_qa_with_sources_chain(
            ChatOpenAI(temperature=0, max_tokens=256,
                       model=self.settings.OPENAI_CHAT_MODEL, request_timeout=120),
            chain_type="stuff",
            document_variable_name="context",
            prompt=PROMPT,
            document_prompt=EXAMPLE_PROMPT
        )
        return doc_chain

    def _load_qa_chain(self, doc_chain):
        """Load QA chain with retriever.
        If use_self_query is True, the retriever will be a SelfQueryRetriever,
        which will extract a metadata filter from question, and add to the vectorstore query.

        NOTE: Can only be used with Pinecone vectorstore.
        """
        use_self_query = self.self_query
        if use_self_query and not isinstance(self.store, Pinecone):
            raise ValueError(
                "SelfQueryRetriever can only be used with Pinecone vectorstore")
        if use_self_query:
            metadata_field_info = [
                AttributeInfo(
                    name="course",
                    description="A course code for a course",
                    type="string"
                )]
            document_content_description = "Brief description of a course"
            llm = OpenAI(temperature=0, model_name='text-davinci-002')
            retriever = SelfQueryRetriever.from_llm(llm, self.store, document_content_description,
                                                    metadata_field_info, verbose=True)
            qa_chain = RetrievalQAWithSourcesChain(combine_documents_chain=doc_chain,
                                                   retriever=retriever,
                                                   return_source_documents=False)
        else:
            qa_chain = RetrievalQAWithSourcesChain(combine_documents_chain=doc_chain,
                                                   retriever=self.store.as_retriever(),
                                                   return_source_documents=False)
        return qa_chain

    def course_exists(self, course: str):
        course = course.upper()
        exists = course in self.courses
        if exists:
            logger.info(f'Course {course} exists')
            return True
        else:
            logger.info(f'Course {course} does not exist')
            return False


if __name__ == '__main__':
    state = State()
    print(state.settings)
