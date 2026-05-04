from abc import ABC, abstractmethod
from typing import List, Dict

class BaseLLM(ABC):
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> dict:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass