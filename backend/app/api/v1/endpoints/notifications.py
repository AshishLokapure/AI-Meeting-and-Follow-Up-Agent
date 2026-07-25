from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_verified_user, require_roles
from app.database import get_db
from app.models import User
from app.models.notification_log import NotificationLog
from app.workers.email_tasks import (
    run_daily_reminders,
    run_deadline_reminders,
    run_escalations,
    send_custom_email,
    send_meeting_summary_email,
    send_task_assignment_email,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


class CustomEmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str
    task_id: str | None = None


class NotificationLogOut(BaseModel):
    id: str
    recipient_email: str
    subject: str
    template_name: str
    delivery_status: str
    retry_count: int
    created_at: str

    model_config = {"from_attributes": True}


@router.post("/send-custom", status_code=status.HTTP_202_ACCEPTED)
def send_custom(
    payload: CustomEmailRequest,
    current_user: User = Depends(get_current_verified_user),
) -> dict:
    """Queue a custom notification email."""
    send_custom_email.delay(
        str(payload.to), payload.subject, payload.body,
        user_id=current_user.id, task_id=payload.task_id,
    )
    return {"message": "Email queued for delivery"}


@router.post("/task/{task_id}/send-assignment", status_code=status.HTTP_202_ACCEPTED)
def trigger_task_assignment(
    task_id: str,
    _: User = Depends(require_roles("admin", "manager")),
) -> dict:
    """Manually trigger a task assignment email."""
    send_task_assignment_email.delay(task_id)
    return {"message": "Task assignment email queued"}


@router.post("/meeting/{meeting_id}/send-summary", status_code=status.HTTP_202_ACCEPTED)
def trigger_meeting_summary(
    meeting_id: str,
    _: User = Depends(require_roles("admin", "manager")),
) -> dict:
    """Manually trigger meeting summary email to all participants."""
    send_meeting_summary_email.delay(meeting_id)
    return {"message": "Meeting summary email queued"}


@router.post("/reminders/run-daily", status_code=status.HTTP_202_ACCEPTED)
def trigger_daily_reminders(_: User = Depends(require_roles("admin"))) -> dict:
    """Manually trigger the daily reminder sweep."""
    run_daily_reminders.delay()
    return {"message": "Daily reminder sweep queued"}


@router.post("/reminders/run-deadline", status_code=status.HTTP_202_ACCEPTED)
def trigger_deadline_reminders(_: User = Depends(require_roles("admin"))) -> dict:
    """Manually trigger the deadline reminder sweep."""
    run_deadline_reminders.delay()
    return {"message": "Deadline reminder sweep queued"}


@router.post("/escalations/run", status_code=status.HTTP_202_ACCEPTED)
def trigger_escalations(_: User = Depends(require_roles("admin"))) -> dict:
    """Manually trigger the escalation sweep."""
    run_escalations.delay()
    return {"message": "Escalation sweep queued"}


@router.get("/logs", response_model=list[NotificationLogOut])
def get_notification_logs(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
) -> list[NotificationLog]:
    """Retrieve email notification audit logs (admin only)."""
    logs = db.scalars(
        select(NotificationLog)
        .order_by(NotificationLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return [
        NotificationLogOut(
            id=log.id,
            recipient_email=log.recipient_email,
            subject=log.subject,
            template_name=log.template_name,
            delivery_status=log.delivery_status,
            retry_count=log.retry_count,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]


@router.get("/logs/my", response_model=list[NotificationLogOut])
def get_my_notification_logs(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_verified_user),
) -> list[NotificationLog]:
    """Retrieve current user's email notification history."""
    logs = db.scalars(
        select(NotificationLog)
        .where(NotificationLog.user_id == current_user.id)
        .order_by(NotificationLog.created_at.desc())
        .limit(limit)
    ).all()
    return [
        NotificationLogOut(
            id=log.id,
            recipient_email=log.recipient_email,
            subject=log.subject,
            template_name=log.template_name,
            delivery_status=log.delivery_status,
            retry_count=log.retry_count,
            created_at=log.created_at.isoformat(),
        )
        for log in logs
    ]
