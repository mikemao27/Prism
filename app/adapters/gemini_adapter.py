from google import genai
from app.adapters.base import BaseLLMAdapter
from app.config import settings


class GeminiAdapter(BaseLLMAdapter):
    def __init__(self, model_name: str):
        self.client  = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = model_name

    def complete(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        return response.text