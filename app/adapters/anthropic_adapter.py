from anthropic import Anthropic
from app.adapters.base import BaseLLMAdapter
from app.config import settings


class AnthropicAdapter(BaseLLMAdapter):
    def __init__(self, model_name: str):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model_name = model_name

    def complete(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text