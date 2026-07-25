from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_verified_user
from app.database import get_db
from app.models import Meeting
from app.schemas import MeetingPublic, MeetingUploadResponse, TranscriptPublic, TranscriptResponse
from app.services import BackgroundJobService, MeetingService, TranscriptService
from app.workers.tasks import process_meeting_pipeline

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post("/upload", response_model=MeetingUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_meeting(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> MeetingUploadResponse:
    meeting, job, storage_backend = MeetingService.upload_meeting(db=db, user=current_user, file=file, title=title)
    db.commit()
    db.refresh(meeting)

    try:
        async_result = process_meeting_pipeline.delay(job.id)
        job = BackgroundJobService.mark_dispatched(db, job, async_result.id)
    except Exception as exc:
        BackgroundJobService.mark_failed(db, job.id, f"Failed to enqueue Celery job: {exc}")
    db.commit()
    db.refresh(job)

    return MeetingUploadResponse(
        message="Meeting uploaded successfully",
        meeting=MeetingPublic.model_validate(meeting),
        storage_backend=storage_backend,
        job_id=job.id,
        job_status=job.status,
    )


@router.get("/{meeting_id}/transcript", response_model=TranscriptResponse)
def get_transcript(
    meeting_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> TranscriptResponse:
    meeting = db.get(Meeting, meeting_id)
    if meeting is None or meeting.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")

    transcript = TranscriptService.get_meeting_transcript(db, meeting_id)
    if transcript is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transcript not available")

    return TranscriptResponse(
        message="Transcript fetched successfully",
        transcript=TranscriptPublic.model_validate(transcript),
        meeting_status=meeting.status,
    )
