from app.router.classifier import classify_prompt, TaskType
from app.router.selector import select_model

CHEAP_MODELS = {"gpt-4o-mini", "claude-haiku-4-5", "gemini-2.0-flash"}

def test_code_classifier():
    result = classify_prompt("Debug this code")
    assert result == TaskType.CODE

def test_reasoning_classifier():
    result = classify_prompt("Explain why the sky is blue")
    assert result == TaskType.REASONING

def test_creative_classifier():
    result = classify_prompt("Write me a poem")
    assert result == TaskType.CREATIVE

def test_factual_classifier():
    result = classify_prompt("What is the capital of France?")
    assert result == TaskType.FACTUAL

def test_general_classifier():
    result = classify_prompt("Hello")
    assert result == TaskType.GENERAL

def test_select_model():
    no_constraints = select_model(TaskType.CODE)
    low_cost = select_model(TaskType.CODE, {"prefer": "low_cost"})
    low_latency = select_model(TaskType.CODE, {"prefer": "low_latency"})

    assert type(no_constraints) == str and low_cost in CHEAP_MODELS and type(low_latency) == str