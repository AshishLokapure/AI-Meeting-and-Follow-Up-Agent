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

from app.database.base import Base
from app.database.session import engine


def create_all_tables() -> None:
    Base.metadata.create_all(bind=engine)
