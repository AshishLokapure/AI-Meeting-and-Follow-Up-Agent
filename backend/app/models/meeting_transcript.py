from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MeetingTranscript(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "meeting_transcripts"

    meeting_id: Mapped[str] = mapped_column(
        ForeignKey("meetings.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    transcript_text: Mapped[str] = mapped_column(Text, nullable=False)
    cleaned_text: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str | None] = mapped_column(String(20))
    confidence_score: Mapped[float | None] = mapped_column(Float)
    source_uri: Mapped[str | None] = mapped_column(Text)
    word_count: Mapped[int | None] = mapped_column(Integer)
    transcription_model: Mapped[str | None] = mapped_column(String(100))
    duration_seconds: Mapped[float | None] = mapped_column(Float)
    transcript_format: Mapped[str | None] = mapped_column(String(50), default="text/plain", nullable=False)
    transcript_storage_url: Mapped[str | None] = mapped_column(Text)
    speaker_segments: Mapped[list | None] = mapped_column(JSONB)

    meeting = relationship("Meeting", back_populates="transcript")
