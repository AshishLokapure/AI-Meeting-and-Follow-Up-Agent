from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_verified_user
from app.database import get_db
from app.schemas import MeetingPublic, MeetingUploadResponse
from app.services import BackgroundJobService, MeetingService
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
