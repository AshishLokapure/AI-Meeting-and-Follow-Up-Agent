from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MeetingPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    status: str
    recording_url: str | None = None
    recording_filename: str | None = None
    recording_mime_type: str | None = None
    recording_size_bytes: int | None = None
    duration_minutes: int | None = None
    duration_seconds: float | None = None
    owner_id: str
    created_at: datetime
    updated_at: datetime


class MeetingUploadResponse(BaseModel):
    message: str
    meeting: MeetingPublic
    storage_backend: str
    job_id: str
    job_status: str
