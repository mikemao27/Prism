import httpx
import os
from .base import BaseLLM
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

FREE_MODEL = "google/gemma-3-4b-it:free"

class OpenRouterLLM(BaseLLM):
    def __init__(self, model: str = FREE_MODEL):
        self.model = model
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Prism"
        }

        payload = {
            "model": self.model,
            "messages": messages,
        }

        response = httpx.post(self.base_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]
        tokens_used = data.get("usage", {}).get("total_tokens", 0)

        return {
            "content": content,
            "model": self.model,
            "tokens_used": tokens_used
        }

    def get_model_name(self) -> str:
        return self.model