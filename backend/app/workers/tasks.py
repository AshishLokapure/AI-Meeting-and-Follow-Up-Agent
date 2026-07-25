from celery.utils.log import get_task_logger

from app.database.session import SessionLocal
from app.models import Meeting
from app.models.enums import MeetingStatus
from app.services import BackgroundJobService
from app.workers.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="app.workers.tasks.process_meeting_pipeline", bind=True)
def process_meeting_pipeline(self, job_id: str) -> dict:
    db = SessionLocal()
    try:
        job = BackgroundJobService.mark_started(db, job_id)
        if job is None:
            db.commit()
            return {"job_id": job_id, "status": "missing"}

        meeting = db.get(Meeting, job.meeting_id) if job.meeting_id else None
        if meeting is not None:
            meeting.status = MeetingStatus.processing.value

        result = {
            "job_id": job_id,
            "meeting_id": job.meeting_id,
            "status": "processing",
            "message": "Meeting queued for AI processing",
        }
        BackgroundJobService.mark_succeeded(db, job_id, result=result)
        db.commit()
        return result
    except Exception as exc:
        db.rollback()
        BackgroundJobService.mark_failed(db, job_id, str(exc))
        db.commit()
        logger.exception("Meeting pipeline job failed")
        raise
    finally:
        db.close()
