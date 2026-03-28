from fastapi import APIRouter
from fastapi import HTTPException
from app.router.policies import MODEL_REGISTRY
from app.schemas.query import QueryRequest, QueryResponse
from app.router.classifier import classify_prompt
from app.router.selector import select_model
from app.adapters.openai_adapter import OpenAIAdapter
from app.adapters.anthropic_adapter import AnthropicAdapter
from app.adapters.gemini_adapter import GeminiAdapter
import time
from app.db.session import get_db
from app.models.query_log import QueryLog

router = APIRouter()

ADAPTER_MAP = {
        "gpt-4o": OpenAIAdapter,
        "gpt-4o-mini": OpenAIAdapter,
        "claude-sonnet-4-5": AnthropicAdapter,
        "claude-haiku-4-5": AnthropicAdapter,
        "gemini-2.0-flash": GeminiAdapter,
        "gemini-2.5-pro": GeminiAdapter
    }

@router.post("/query")
def handle_query(request: QueryRequest) -> QueryResponse:
    start_time = time.time()
    task_type = classify_prompt(request.query)
    model_name = select_model(task_type, request.constraints)
    if model_name not in ADAPTER_MAP:
        raise HTTPException(status_code=400, detail=f"Unknown Mode: {model_name}")

    try:
        adapter = ADAPTER_MAP[model_name](model_name)
        response_text = adapter.complete(request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model Call Failed: {str(e)}")

    latency = (time.time() - start_time) * 1000

    db = next(get_db())
    log = QueryLog(
        query=request.query,
        task_type=task_type.value,
        model_used=model_name,
        response=response_text,
        latency_ms=latency,
        estimated_cost=MODEL_REGISTRY[model_name].cost_per_token * len(request.query.split()) * 1.3
    )

    db.add(log)
    db.commit()
    db.close()

    return QueryResponse(
        response=response_text,
        model_used=model_name,
        latency_ms=latency,
        estimated_cost=MODEL_REGISTRY[model_name].cost_per_token * len(request.query.split()) * 1.3
    )