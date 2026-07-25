from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import NotificationChannel, NotificationStatus


class Notification(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "notifications"

    task_id: Mapped[str | None] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), index=True
    )
    recipient_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    channel: Mapped[str] = mapped_column(String(20), default=NotificationChannel.in_app.value, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=NotificationStatus.queued.value, nullable=False)
    subject: Mapped[str | None] = mapped_column(String(255))
    body: Mapped[str | None] = mapped_column(Text)
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    external_reference: Mapped[str | None] = mapped_column(String(255))

    task = relationship("Task", back_populates="notifications")
    recipient = relationship("User", back_populates="notifications")
    reminder_logs = relationship("ReminderLog", back_populates="notification", cascade="all, delete-orphan")
