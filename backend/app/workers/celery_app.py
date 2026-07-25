from celery import Celery

from app.core.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "ai_meeting_agent",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # Local/dev convenience: run jobs in-process when Redis/Celery worker isn't up.
    task_always_eager=settings.environment == "development",
    task_eager_propagates=True,
)
