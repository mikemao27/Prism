from enum import Enum

class TaskType(Enum):
    # These are the different types of tasks. We may need to add more types in the future.
    CODE = "code"
    REASONING = "reasoning"
    CREATIVE = "creative"
    FACTUAL = "factual"
    GENERAL = "general"

def classify_prompt(prompt: str) -> TaskType:
    # For now, we will do key word matching. This isn't great in practice, but it's a start.
    # In the future, we may want to use a more sophisticated method, such as a machine learning model, to classify the prompts.
    # Such a model would simply be a classification model.
    prompt = prompt.lower()

    code_keywords = ["code", "debug", "program", "algorithm", "function", "class"]
    reasoning_keywords = ["explain", "why", "analyze", "compare", "summarize"]
    creative_keywords = ["write", "story", "poem", "essay", "produce", "generate", "create"]
    factual_keywords = ["what", "who", "when", "where", "how", "define", "describe"]

    if any(keyword in prompt for keyword in code_keywords):
        return TaskType.CODE
    elif any(keyword in prompt for keyword in reasoning_keywords):
        return TaskType.REASONING
    elif any(keyword in prompt for keyword in creative_keywords):
        return TaskType.CREATIVE
    elif any(keyword in prompt for keyword in factual_keywords):
        return TaskType.FACTUAL
    else:
        return TaskType.GENERAL
