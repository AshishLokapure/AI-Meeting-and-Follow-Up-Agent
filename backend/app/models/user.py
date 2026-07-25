from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="member", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    # Enterprise fields
    employee_id: Mapped[str | None] = mapped_column(String(50), unique=True, index=True)
    department: Mapped[str | None] = mapped_column(String(100))
    designation: Mapped[str | None] = mapped_column(String(100))
    manager_id: Mapped[str | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)

    manager = relationship("User", remote_side="User.id", foreign_keys=[manager_id])
    meetings = relationship("Meeting", back_populates="owner", cascade="all, delete-orphan")
    tasks = relationship("Task", foreign_keys="Task.assignee_id", back_populates="assignee")
    notifications = relationship("Notification", back_populates="recipient")
    task_activities = relationship("TaskActivity", back_populates="actor")
    escalation_logs_as_employee = relationship(
        "EscalationLog",
        foreign_keys="EscalationLog.employee_id",
        back_populates="employee",
    )
    escalation_logs_as_manager = relationship(
        "EscalationLog",
        foreign_keys="EscalationLog.manager_id",
        back_populates="manager",
    )
    ai_logs = relationship("AILog", back_populates="user")
    system_logs = relationship("SystemLog", back_populates="user")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    email_verification_tokens = relationship("EmailVerificationToken", back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")
