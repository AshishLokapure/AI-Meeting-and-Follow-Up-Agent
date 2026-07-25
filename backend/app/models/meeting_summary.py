from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MeetingSummary(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "meeting_summaries"

    meeting_id: Mapped[str] = mapped_column(
        ForeignKey("meetings.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    decisions: Mapped[list | None] = mapped_column(JSONB)
    action_items: Mapped[list | None] = mapped_column(JSONB)
    risks: Mapped[list | None] = mapped_column(JSONB)
    model_name: Mapped[str | None] = mapped_column(String(100))
    analysis_payload: Mapped[dict | None] = mapped_column(JSONB)

    meeting = relationship("Meeting", back_populates="summary")
