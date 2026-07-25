from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class SystemLog(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "system_logs"

    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="info")
    service: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    correlation_id: Mapped[str | None] = mapped_column(String(100), index=True)
    request_path: Mapped[str | None] = mapped_column(String(255))
    request_method: Mapped[str | None] = mapped_column(String(20))
    context: Mapped[dict | None] = mapped_column(JSONB)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user = relationship("User", back_populates="system_logs")
