from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MeetingTranscript


class TranscriptService:
    @classmethod
    def get_meeting_transcript(cls, db: Session, meeting_id: str) -> MeetingTranscript | None:
        return db.scalar(select(MeetingTranscript).where(MeetingTranscript.meeting_id == meeting_id))
