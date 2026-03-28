from dataclasses import dataclass, field
from app.router.classifier import TaskType

@dataclass
class ModelProfile:
    name: str
    cost_per_token: float
    avg_latency: float
    quality_score: float
    strengths: list[TaskType] = field(default_factory=list)

MODEL_REGISTRY = {
    "gpt-4o": ModelProfile("gpt-4o", 0.00375, 1200, 0.92, [TaskType.CODE, TaskType.REASONING, TaskType.FACTUAL]),
    "gpt-4o-mini": ModelProfile("gpt-4o-mini", 0.000225, 500, 0.75, [TaskType.FACTUAL, TaskType.GENERAL]),
    "claude-sonnet-4-5": ModelProfile("claude-sonnet-4-5", 0.003, 1000, 0.90, [TaskType.REASONING, TaskType.CREATIVE, TaskType.CODE]),
    "claude-haiku-4-5": ModelProfile("claude-haiku-4-5", 0.0002, 400, 0.72, [TaskType.FACTUAL, TaskType.GENERAL, TaskType.CREATIVE]),
    "gemini-2.0-flash": ModelProfile("gemini-2.0-flash", 0.0000875, 600, 0.82,[TaskType.FACTUAL, TaskType.GENERAL, TaskType.CODE]),
    "gemini-2.5-pro": ModelProfile("gemini-2.5-pro", 0.00125, 1500, 0.90, [TaskType.REASONING, TaskType.CODE, TaskType.FACTUAL])
}