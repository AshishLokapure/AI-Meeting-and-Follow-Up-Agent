from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="member", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    meetings = relationship("Meeting", back_populates="owner", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="assignee")
    notifications = relationship("Notification", back_populates="recipient")
    task_activities = relationship("TaskActivity", back_populates="actor")
    ai_logs = relationship("AILog", back_populates="user")
    system_logs = relationship("SystemLog", back_populates="user")
