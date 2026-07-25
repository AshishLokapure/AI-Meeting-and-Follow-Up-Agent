from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

class MeetingParticipantPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    email: str | None = None
    role: str | None = None

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
    meeting_date: date | None = None
    start_time: datetime | None = None
    agenda: str | None = None
    created_at: datetime
    updated_at: datetime

class MeetingDetailPublic(MeetingPublic):
    participants: list[MeetingParticipantPublic] = []
    summary_text: str | None = None
    action_items_count: int = 0
    decisions_count: int = 0

class MeetingUploadResponse(BaseModel):
    message: str
    meeting: MeetingPublic
    storage_backend: str
    job_id: str
    job_status: str

