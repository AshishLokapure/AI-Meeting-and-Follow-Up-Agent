from celery.utils.log import get_task_logger

from app.core.settings import get_settings
from app.database.session import SessionLocal
from app.models import Meeting
from app.models.enums import MeetingStatus
from app.services import AIAnalysisService, BackgroundJobService, TranscriptProcessingService, TranscriptionService
from app.services.diarization_service import diarize_audio, merge_with_transcript
from app.services.ffmpeg_service import convert_video_to_audio
from app.services.whisper_service import transcribe_audio
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
        settings = get_settings()
        pipeline_result = None
        video_path, should_cleanup = TranscriptionService.resolve_audio_path(meeting)
        try:
            conversion = convert_video_to_audio(video_path)
            whisper_result = transcribe_audio(conversion.path)
            transcript_text = whisper_result.text
            speaker_segments = []
            if settings.diarization_enabled:
                try:
                    diarization = diarize_audio(conversion.path)
                    transcript_text, speaker_segments = merge_with_transcript(whisper_result.segments, diarization)
                except Exception as exc:
                    logger.warning("Speaker diarization skipped: %s", exc)
            meeting.duration_seconds = conversion.duration_seconds
            meeting.duration_minutes = max(1, round(conversion.duration_seconds / 60))
            meeting.source_metadata = {
                **(meeting.source_metadata or {}),
                "audio_url": f"/uploads/audio/{conversion.path.name}",
                "audio_storage_key": f"audio/{conversion.path.name}",
            }
            transcript_result = TranscriptionService.persist_transcript(
                db,
                meeting,
                transcript_text,
                language=whisper_result.language,
                confidence_score=whisper_result.confidence_score,
                model_name=whisper_result.model_name,
                speaker_segments=speaker_segments,
            )
        finally:
            if should_cleanup:
                video_path.unlink(missing_ok=True)

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
            "key_notes": (pipeline_result or {}).get("key_notes", []),
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
