from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
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

    meeting = relationship("Meeting", back_populates="transcript")
