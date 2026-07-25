from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import TaskPriority, TaskStatus


class Task(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "tasks"

    meeting_id: Mapped[str] = mapped_column(
        ForeignKey("meetings.id", ondelete="CASCADE"), index=True, nullable=False
    )
    assignee_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    assigned_by_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(20), default=TaskPriority.medium.value, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=TaskStatus.pending.value, nullable=False)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completion_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reminder_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reminder_interval_hours: Mapped[int] = mapped_column(Integer, default=24, nullable=False)
    source_excerpt: Mapped[str | None] = mapped_column(Text)
    extracted_metadata: Mapped[dict | None] = mapped_column(JSONB)

    meeting = relationship("Meeting", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="tasks")
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])
    activities = relationship("TaskActivity", back_populates="task", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="task")
    escalations = relationship("EscalationLog", back_populates="task", cascade="all, delete-orphan")
