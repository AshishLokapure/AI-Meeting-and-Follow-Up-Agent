from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import MeetingStatus


class Meeting(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "meetings"

    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    agenda: Mapped[str | None] = mapped_column(Text)
    meeting_date: Mapped[date | None] = mapped_column(Date)
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default=MeetingStatus.uploaded.value, nullable=False)
    recording_url: Mapped[str | None] = mapped_column(Text)
    source_metadata: Mapped[dict | None] = mapped_column(JSONB)

    owner = relationship("User", back_populates="meetings")
    participants = relationship("MeetingParticipant", back_populates="meeting", cascade="all, delete-orphan")
    transcript = relationship("MeetingTranscript", back_populates="meeting", uselist=False, cascade="all, delete-orphan")
    summary = relationship("MeetingSummary", back_populates="meeting", uselist=False, cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="meeting", cascade="all, delete-orphan")
    ai_logs = relationship("AILog", back_populates="meeting")
