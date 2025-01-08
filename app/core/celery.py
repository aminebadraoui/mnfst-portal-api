from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "mnfst_labs",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.features.research_hub.tasks.analysis"
    ]
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
) 