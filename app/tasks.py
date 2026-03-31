from app.worker import celery_app
from app.db.session import SessionLocal
from app.models.query_log import QueryLog

@celery_app.task
def log_query_task(query: str, task_type: str, model_used: str, response: str, latency_ms: float, estimated_cost: float):
    db = SessionLocal()
    log = QueryLog(
        query=query,
        task_type=task_type,
        model_used=model_used,
        response=response,
        latency_ms=latency_ms,
        estimated_cost=estimated_cost
    )
    db.add(log)
    db.commit()
    db.close()
