from llm.openrouter import OpenRouterLLM, FREE_MODEL
from typing import Optional
import json

def score_models(message: str, available_models: list[dict]) -> str:
    if not available_models:
        return FREE_MODEL
    
    provider_list = list({m["provider"] for m in available_models})

    prompt = f"""You are a routing assistant. Given the user message, decide which LLM provider is best suited for it.

    Available providers: {provider_list}

    Provider strengths:
    - anthropic: coding, reasoning, creative writing, nuanced tasks
    - openai: math, logic, general purpose, structured output
    - google: long documents, factual lookup, summarization
    - openrouter: general fallback

    User message: "{message}"

    Respond ONLY with a JSON object like this, no explanation:
    {{"provider": "anthropic", "reason": "contains code"}}"""

    try:
        llm = OpenRouterLLM()
        response = llm.chat([{"role": "user", "content": prompt}])
        raw = response["content"].strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        chosen_provider = data.get("provider", "openrouter")

        for model_entry in available_models:
            if model_entry["provider"] == chosen_provider:
                return model_entry["model"]
        
        return FREE_MODEL
    except Exception as e:
        return FREE_MODEL


def get_llm(model_name: Optional[str] = None):
    if model_name is None:
        model_name = FREE_MODEL
    return OpenRouterLLM(model=model_name)

def has_sufficient_credits(model_entry: dict) -> bool:
    if not model_entry.get("api_key"):
        return False
    balance = model_entry.get("credit_balance")
    if balance is None:
        return True
    try:
        amount = float(balance.replace("$", "").strip())
        return amount > 0
    except ValueError:
        return True

def route(message: str, available_models: list[dict]) -> tuple[str, object]:
    eligible_models = [m for m in available_models if has_sufficient_credits(m)]
    model_name = score_models(message, eligible_models)
    llm = get_llm(model_name)
    return model_name, llm