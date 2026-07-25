from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_verified_user
from app.database import get_db
from app.schemas import MeetingPublic, MeetingUploadResponse
from app.services import MeetingService

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post("/upload", response_model=MeetingUploadResponse, status_code=status.HTTP_201_CREATED)
def upload_meeting(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> MeetingUploadResponse:
    meeting, storage_backend = MeetingService.upload_meeting(db=db, user=current_user, file=file, title=title)
    db.commit()
    db.refresh(meeting)
    return MeetingUploadResponse(
        message="Meeting uploaded successfully",
        meeting=MeetingPublic.model_validate(meeting),
        storage_backend=storage_backend,
    )
