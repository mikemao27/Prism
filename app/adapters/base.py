from abc import ABC, abstractmethod
from app.router.classifier import classify_prompt
from app.router.selector import select_model

class BaseLLMAdapter(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> str:
        pass