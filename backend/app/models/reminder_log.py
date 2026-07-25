from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import ReminderStatus


class ReminderLog(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "reminder_logs"

    notification_id: Mapped[str | None] = mapped_column(
        ForeignKey("notifications.id", ondelete="CASCADE"), index=True
    )
    task_id: Mapped[str | None] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), default=ReminderStatus.scheduled.value, nullable=False)
    attempt_number: Mapped[int] = mapped_column(default=1, nullable=False)
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    response_message: Mapped[str | None] = mapped_column(Text)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    notification = relationship("Notification", back_populates="reminder_logs")
    task = relationship("Task")
