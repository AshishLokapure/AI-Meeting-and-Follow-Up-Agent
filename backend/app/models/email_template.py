from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class EmailTemplate(Base, TimestampMixin, UUIDPrimaryKeyMixin):
    __tablename__ = "email_templates"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    template_type: Mapped[str] = mapped_column(String(50), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    variables: Mapped[dict | None] = mapped_column(JSONB)
