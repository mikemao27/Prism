import google.generativeai as genai
from app.adapters.base import BaseLLMAdapter
from app.config import settings


class GeminiAdapter(BaseLLMAdapter):
    def __init__(self, model_name: str):
        genai.configure(api_key = settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name)

    def complete(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text