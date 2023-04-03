from dataclasses import dataclass
from enum import Enum

class ModelType(Enum):
    GPT3 = "gpt3"
    CHAT_GPT3 = "chat_gpt3"

@dataclass
class Model:
    name: str
    type: ModelType