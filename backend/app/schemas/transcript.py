from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TranscriptPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    meeting_id: str
    transcript_text: str
    cleaned_text: str | None = None
    language: str | None = None
    confidence_score: float | None = None
    source_uri: str | None = None
    word_count: int | None = None
    transcription_model: str | None = None
    duration_seconds: float | None = None
    transcript_format: str | None = None
    transcript_storage_url: str | None = None
    speaker_segments: list[dict] | None = None
    created_at: datetime
    updated_at: datetime


class TranscriptResponse(BaseModel):
    message: str
    transcript: TranscriptPublic
    meeting_status: str
