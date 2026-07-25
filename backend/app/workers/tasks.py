from celery.utils.log import get_task_logger

from app.database.session import SessionLocal
from app.models import Meeting
from app.models.enums import MeetingStatus
from app.services import AIAnalysisService, BackgroundJobService, TranscriptProcessingService, TranscriptionService
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
        if meeting is None:
            BackgroundJobService.mark_failed(db, job_id, "Meeting not found")
            db.commit()
            return {"job_id": job_id, "status": "failed", "message": "Meeting not found"}

        meeting.status = MeetingStatus.processing.value
        transcript_result = TranscriptionService.transcribe_meeting(db, meeting)
        cleanup_result = TranscriptProcessingService.clean_meeting_transcript(
            db,
            meeting,
            transcript_result.transcript_text,
        )
        analysis_result = AIAnalysisService.analyze_meeting(db, meeting)

        result = {
            "job_id": job_id,
            "meeting_id": meeting.id,
            "status": "analyzed",
            "message": "Meeting transcribed, cleaned, and analyzed successfully",
            "transcription_model": transcript_result.transcription_model,
            "word_count": transcript_result.word_count,
            "language": transcript_result.language,
            "confidence_score": transcript_result.confidence_score,
            "transcript_storage_url": transcript_result.transcript_storage_url,
            "cleaned_paragraphs": cleanup_result.paragraph_count,
            "removed_fillers": cleanup_result.removed_fillers,
            "analysis_model": analysis_result.model_name,
            "summary": analysis_result.executive_summary,
            "decisions": analysis_result.decisions,
            "action_items": analysis_result.action_items,
            "risks": analysis_result.risks,
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
