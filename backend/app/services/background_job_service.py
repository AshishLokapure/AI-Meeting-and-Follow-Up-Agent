from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import BackgroundJob


class BackgroundJobService:
    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)

    @classmethod
    def create_meeting_pipeline_job(cls, db: Session, meeting) -> BackgroundJob:
        job = BackgroundJob(
            meeting_id=meeting.id,
            job_type="meeting_pipeline",
            status="queued",
            payload={
                "meeting_id": meeting.id,
                "owner_id": meeting.owner_id,
            },
            queued_at=cls._utcnow(),
            attempts=0,
        )
        db.add(job)
        db.flush()
        return job

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
