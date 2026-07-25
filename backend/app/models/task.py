from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
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
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(20), default=TaskPriority.medium.value, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=TaskStatus.pending.value, nullable=False)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_excerpt: Mapped[str | None] = mapped_column(Text)
    extracted_metadata: Mapped[dict | None] = mapped_column(JSONB)

    meeting = relationship("Meeting", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")
    activities = relationship("TaskActivity", back_populates="task", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="task")
