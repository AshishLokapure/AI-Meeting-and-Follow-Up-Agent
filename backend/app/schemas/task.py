from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    meeting_id: str
    assignee_id: str | None = None
    title: str
    description: str | None = None
    priority: str
    status: str
    due_date: datetime | None = None
    source_excerpt: str | None = None
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    tasks: list[TaskPublic]
    total: int


class TaskUpdateRequest(BaseModel):
    status: str | None = None
    priority: str | None = None
    title: str | None = None
    description: str | None = None


class DashboardStats(BaseModel):
    total_meetings: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    overdue_tasks: int = 0
    in_progress_tasks: int = 0


class MeetingListResponse(BaseModel):
    meetings: list = []
    total: int = 0
