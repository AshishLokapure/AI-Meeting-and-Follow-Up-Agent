from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_verified_user
from app.database import get_db
from app.models import Meeting, Task
from app.schemas import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> DashboardStats:
    total_meetings = db.query(Meeting).filter(Meeting.owner_id == current_user.id).count()

    tasks_query = (
        db.query(Task)
        .join(Meeting, Task.meeting_id == Meeting.id)
        .filter(Meeting.owner_id == current_user.id)
    )

    total_tasks = tasks_query.count()
    completed_tasks = tasks_query.filter(Task.status == "completed").count()
    pending_tasks = tasks_query.filter(Task.status == "pending").count()
    overdue_tasks = tasks_query.filter(Task.status == "overdue").count()
    in_progress_tasks = tasks_query.filter(Task.status == "in_progress").count()

    return DashboardStats(
        total_meetings=total_meetings,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        in_progress_tasks=in_progress_tasks,
    )
