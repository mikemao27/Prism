from celery import Celery
from app.config import settings

celery_app = Celery(
    "prism",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.imports = ["app.tasks"]