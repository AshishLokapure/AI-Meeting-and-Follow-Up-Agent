from celery import Celery

from app.core.settings import get_settings
from app.workers.scheduler import BEAT_SCHEDULE

settings = get_settings()

celery_app = Celery(
    "ai_meeting_agent",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks", "app.workers.email_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    beat_schedule=BEAT_SCHEDULE,
    # Local/dev convenience: run jobs in-process when Redis/Celery worker isn't up.
    task_always_eager=settings.environment == "development",
    task_eager_propagates=True,
)
