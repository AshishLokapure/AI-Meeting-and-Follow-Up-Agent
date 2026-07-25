from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_verified_user
from app.database import get_db
from app.models import Meeting, Task
from app.schemas import TaskListResponse, TaskPublic, TaskUpdateRequest

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
def list_tasks(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
    status_filter: str | None = Query(default=None, alias="status"),
    priority: str | None = Query(default=None),
    q: str | None = Query(default=None, max_length=200),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> TaskListResponse:
    # Tasks belong to meetings owned by the current user
    base = (
        db.query(Task)
        .join(Meeting, Task.meeting_id == Meeting.id)
        .filter(Meeting.owner_id == current_user.id)
    )

    if status_filter:
        base = base.filter(Task.status == status_filter)
    if priority:
        base = base.filter(Task.priority == priority)
    if q:
        base = base.filter(Task.title.ilike(f"%{q}%"))

    total = base.count()
    tasks = base.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()

    return TaskListResponse(
        tasks=[TaskPublic.model_validate(t) for t in tasks],
        total=total,
    )


@router.get("/{task_id}", response_model=TaskPublic)
def get_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> TaskPublic:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Verify the task belongs to a meeting owned by the user
    meeting = db.get(Meeting, task.meeting_id)
    if meeting is None or meeting.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return TaskPublic.model_validate(task)


@router.patch("/{task_id}", response_model=TaskPublic)
def update_task(
    task_id: str,
    payload: TaskUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> TaskPublic:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    meeting = db.get(Meeting, task.meeting_id)
    if meeting is None or meeting.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return TaskPublic.model_validate(task)
