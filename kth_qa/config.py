from pydantic import BaseSettings

from kth_qa.gpt import GPT, set_openai_key
from kth_qa.magic import VectorIndex
from kth_qa.model_types import Model, ModelType


class Settings(BaseSettings):
    OPENAI_API_KEY: str = 'OPENAI_API_KEY'
    OPENAI_MODEL: str = 'OPENAI_MODEL'
    OPENAI_CHAT_MODEL: str = 'OPENAI_CHAT_MODEL'
    class Config:
        env_file = '../.env'



class Config:
    gpt = GPT
    model: Model
    settings: Settings
    index: VectorIndex

    def __init__(self, debug=False):
        self.debug = debug
        self.settings = Settings()

        # OPENAI
        set_openai_key(self.settings.OPENAI_API_KEY)
        self.model = Model(self.settings.OPENAI_CHAT_MODEL, ModelType.CHAT_GPT3)
        # model = Model(settings.OPENAI_MODEL, ModelType.GPT3)

        self.gpt = GPT(engine=self.model.name, temperature=0.5, max_tokens=10000)

        # Langchain
        self.index = VectorIndex(debug)