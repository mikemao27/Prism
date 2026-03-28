from app.router.classifier import TaskType
from app.router.policies import MODEL_REGISTRY

def select_model(task: TaskType, constraints: dict | None = None) -> str:
    max_utility = float("-inf")
    optimal_model = None

    prefer = constraints.get("prefer") if constraints else None
    
    if prefer == "low_cost":
        alpha, beta = 0.8, 0.2
    elif prefer == "low_latency":
        alpha, beta = 0.2, 0.8
    else:
        alpha, beta = 0.5, 0.5

    for model in MODEL_REGISTRY:
        quality_score = MODEL_REGISTRY[model].quality_score
        cost_per_token = MODEL_REGISTRY[model].cost_per_token
        avg_latency = MODEL_REGISTRY[model].avg_latency

        utility = quality_score - alpha * cost_per_token - beta * (avg_latency / 1000)

        strengths = MODEL_REGISTRY[model].strengths
        if task in strengths:
            utility += 0.1

        if utility > max_utility:
            max_utility = utility
            optimal_model = model
    
    return optimal_model
