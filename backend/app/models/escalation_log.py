from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class EscalationLog(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "escalation_logs"

    task_id: Mapped[str] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    employee_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    manager_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    escalation_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    escalated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)

    task = relationship("Task", back_populates="escalations")
    employee = relationship("User", foreign_keys=[employee_id], back_populates="escalation_logs_as_employee")
    manager = relationship("User", foreign_keys=[manager_id], back_populates="escalation_logs_as_manager")
