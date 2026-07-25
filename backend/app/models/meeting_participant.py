from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MeetingParticipant(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "meeting_participants"

    meeting_id: Mapped[str] = mapped_column(
        ForeignKey("meetings.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    participant_name: Mapped[str] = mapped_column(String(150), nullable=False)
    participant_email: Mapped[str | None] = mapped_column(String(255), index=True)
    participant_role: Mapped[str | None] = mapped_column(String(100))

    meeting = relationship("Meeting", back_populates="participants")
    user = relationship("User")
