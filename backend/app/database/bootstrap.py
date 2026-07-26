from app.models import (  # noqa: F401
    AILog,
    BackgroundJob,
    BackgroundJobStatus,
    EmailVerificationToken,
    Meeting,
    MeetingParticipant,
    MeetingSummary,
    MeetingTranscript,
    Notification,
    PasswordResetToken,
    RefreshToken,
    ReminderLog,
    SystemLog,
    Task,
    TaskActivity,
    User,
)

from sqlalchemy import text
from app.database.base import Base
from app.database.session import engine


def create_all_tables() -> None:
    Base.metadata.create_all(bind=engine)
    if engine.dialect.name == "postgresql":
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE meeting_transcripts ADD COLUMN IF NOT EXISTS speaker_segments JSONB"))
