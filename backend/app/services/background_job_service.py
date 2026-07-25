from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import BackgroundJob


class BackgroundJobService:
    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)

    @classmethod
    def mark_dispatched(cls, db: Session, job: BackgroundJob, celery_task_id: str) -> BackgroundJob:
        job.celery_task_id = celery_task_id
        return job

    @classmethod
    def mark_started(cls, db: Session, job_id: str) -> BackgroundJob | None:
        job = db.get(BackgroundJob, job_id)
        if job is None:
            return None
        job.status = "started"
        job.started_at = cls._utcnow()
        job.attempts += 1
        return job

    @classmethod
    def mark_succeeded(cls, db: Session, job_id: str, result: dict | None = None) -> BackgroundJob | None:
        job = db.get(BackgroundJob, job_id)
        if job is None:
            return None
        job.status = "succeeded"
        job.result = result
        job.finished_at = cls._utcnow()
        return job

    @classmethod
    def mark_failed(cls, db: Session, job_id: str, error_message: str) -> BackgroundJob | None:
        job = db.get(BackgroundJob, job_id)
        if job is None:
            return None
        job.status = "failed"
        job.error_message = error_message
        job.finished_at = cls._utcnow()
        return job
