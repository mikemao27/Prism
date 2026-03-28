from openai import OpenAI
from app.adapters.base import BaseLLMAdapter
from app.config import settings


class OpenAIAdapter(BaseLLMAdapter):
    def __init__(self, model_name: str):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model_name = model_name

    def complete(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content