from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MeetingAnalysisPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    meeting_id: str
    executive_summary: str
    decisions: list | None = None
    action_items: list | None = None
    risks: list | None = None
    model_name: str | None = None
    analysis_payload: dict | None = None
    created_at: datetime
    updated_at: datetime


class MeetingAnalysisResponse(BaseModel):
    message: str
    analysis: MeetingAnalysisPublic
    meeting_status: str
