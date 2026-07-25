from datetime import datetime, timezone

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.settings import get_settings
from app.models import Meeting, User
from app.utils import store_meeting_audio


class MeetingService:
    @staticmethod
    def _utcnow() -> datetime:
        return datetime.now(timezone.utc)

    @classmethod
    def upload_meeting(cls, db: Session, user: User, file: UploadFile, title: str | None = None) -> tuple[Meeting, str]:
        stored_file = store_meeting_audio(file)
        meeting = Meeting(
            owner_id=user.id,
            title=title.strip() if title else file.filename or "Untitled Meeting",
            status="uploaded",
            recording_url=stored_file.url,
            recording_filename=stored_file.filename,
            recording_mime_type=stored_file.content_type,
            recording_size_bytes=stored_file.size_bytes,
            duration_minutes=max(1, round(stored_file.size_bytes / 1024 / 1024)),
            source_metadata={
                "storage_backend": get_settings().storage_backend,
                "uploaded_at": cls._utcnow().isoformat(),
                "original_filename": file.filename,
                "storage_key": stored_file.storage_key,
            },
        )
        db.add(meeting)
        db.flush()
        return meeting, get_settings().storage_backend
