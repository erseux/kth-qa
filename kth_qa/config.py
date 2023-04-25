from pydantic import BaseSettings

from kth_qa.gpt import GPT, set_openai_key
from kth_qa.magic import VectorIndex
from kth_qa.model_types import Model, ModelType

from pydantic import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str = 'OPENAI_API_KEY'
    OPENAI_MODEL: str = 'OPENAI_MODEL'
    OPENAI_CHAT_MODEL: str = 'OPENAI_CHAT_MODEL'
    class Config:
        env_file = 'C:\\Users\\46705\\Documents\\Search_engines\\project_work\\kth-qa\\kth_qa\\.env'


settings = Settings()

# OPENAI
set_openai_key(settings.OPENAI_API_KEY)
model = Model(settings.OPENAI_CHAT_MODEL, ModelType.CHAT_GPT3)
# model = Model(settings.OPENAI_MODEL, ModelType.GPT3)

gpt = GPT(engine=model.name, temperature=0.5, max_tokens=10000)

# Langchain
index = VectorIndex()

class Config:
    gpt = gpt
    model = model
    settings = settings
    index = index