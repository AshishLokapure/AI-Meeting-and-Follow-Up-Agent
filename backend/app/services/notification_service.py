from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EscalationLog, MeetingParticipant, ReminderLog, Task, User
from app.models.enums import ReminderStatus, TaskStatus
from app.models.meeting_summary import MeetingSummary
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class NotificationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.email = EmailService()

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _get_user(self, user_id: str | None) -> User | None:
        return self.db.get(User, user_id) if user_id else None

    def _record_reminder(
        self,
        task_id: str,
        status: str,
        next_reminder: datetime | None,
        attempt: int = 1,
        response: str = "",
    ) -> None:
        log = ReminderLog(
            task_id=task_id,
            status=status,
            attempt_number=attempt,
            sent_at=_utcnow(),
            response_message=response,
            next_retry_at=next_reminder,
        )
        self.db.add(log)
        self.db.flush()

    def _record_escalation(self, task: Task, manager_id: str | None) -> None:
        log = EscalationLog(
            task_id=task.id,
            employee_id=task.assignee_id,
            manager_id=manager_id,
            escalation_level=1,
            reason="Task overdue",
            email_sent=True,
            escalated_at=_utcnow(),
        )
        self.db.add(log)
        self.db.flush()

    # ── Task assignment ────────────────────────────────────────────────────────

    def notify_task_assigned(self, task: Task) -> dict:
        assignee = self._get_user(task.assignee_id)
        if not assignee:
            return {"success": False, "message": "Assignee not found"}

        assigner = self._get_user(task.assigned_by_id)
        assigner_name = assigner.name if assigner else "System"

        result = self.email.send_task_assignment(
            to=assignee.email,
            assignee_name=assignee.name,
            assigner_name=assigner_name,
            task_title=task.title,
            task_description=task.description or "",
            deadline=task.due_date,
            priority=task.priority,
            task_id=task.id,
            user_id=assignee.id,
        )
        next_reminder = _utcnow() + timedelta(hours=task.reminder_interval_hours)
        self._record_reminder(task.id, ReminderStatus.sent.value if result["success"] else ReminderStatus.failed.value, next_reminder)
        return result

    # ── Daily reminders ────────────────────────────────────────────────────────

    def send_daily_reminders(self) -> list[str]:
        """Called by Celery Beat every 24 h. Returns list of task IDs processed."""
        now = _utcnow()
        tasks = self.db.scalars(
            select(Task)
            .where(Task.status.notin_([TaskStatus.completed.value, TaskStatus.cancelled.value]))
            .where(Task.reminder_enabled.is_(True))
            .where(Task.assignee_id.is_not(None))
        ).all()

        processed: list[str] = []
        for task in tasks:
            # Check if it's time for the next reminder
            last_log = self.db.scalars(
                select(ReminderLog)
                .where(ReminderLog.task_id == task.id)
                .order_by(ReminderLog.sent_at.desc())
                .limit(1)
            ).first()

            if last_log and last_log.next_retry_at and last_log.next_retry_at > now:
                continue  # Not yet due

            assignee = self._get_user(task.assignee_id)
            if not assignee:
                continue

            result = self.email.send_daily_reminder(
                to=assignee.email,
                assignee_name=assignee.name,
                task_title=task.title,
                task_description=task.description or "",
                deadline=task.due_date,
                priority=task.priority,
                task_id=task.id,
                user_id=assignee.id,
            )
            next_reminder = now + timedelta(hours=task.reminder_interval_hours)
            attempt = (last_log.attempt_number + 1) if last_log else 1
            self._record_reminder(
                task.id,
                ReminderStatus.sent.value if result["success"] else ReminderStatus.failed.value,
                next_reminder,
                attempt=attempt,
                response=result.get("smtp_response", ""),
            )
            processed.append(task.id)

        self.db.commit()
        logger.info("Daily reminders: processed %d tasks", len(processed))
        return processed

    # ── Deadline reminders ─────────────────────────────────────────────────────

    def send_deadline_reminders(self) -> list[str]:
        """Send reminders for tasks due within 24 hours."""
        now = _utcnow()
        window = now + timedelta(hours=24)
        tasks = self.db.scalars(
            select(Task)
            .where(Task.status.notin_([TaskStatus.completed.value, TaskStatus.cancelled.value]))
            .where(Task.due_date.between(now, window))
            .where(Task.assignee_id.is_not(None))
        ).all()

        processed: list[str] = []
        for task in tasks:
            assignee = self._get_user(task.assignee_id)
            if not assignee:
                continue
            hours_remaining = max(0, int((task.due_date - now).total_seconds() // 3600))
            result = self.email.send_deadline_reminder(
                to=assignee.email,
                assignee_name=assignee.name,
                task_title=task.title,
                task_description=task.description or "",
                deadline=task.due_date,
                hours_remaining=hours_remaining,
                task_id=task.id,
                user_id=assignee.id,
            )
            self._record_reminder(
                task.id,
                ReminderStatus.sent.value if result["success"] else ReminderStatus.failed.value,
                None,
                response=result.get("smtp_response", ""),
            )
            processed.append(task.id)

        self.db.commit()
        return processed

    # ── Escalations ────────────────────────────────────────────────────────────

    def send_escalations(self) -> list[str]:
        """Escalate overdue tasks to manager. Runs daily."""
        now = _utcnow()
        tasks = self.db.scalars(
            select(Task)
            .where(Task.status.notin_([TaskStatus.completed.value, TaskStatus.cancelled.value]))
            .where(Task.due_date < now)
            .where(Task.assignee_id.is_not(None))
        ).all()

        processed: list[str] = []
        for task in tasks:
            assignee = self._get_user(task.assignee_id)
            if not assignee:
                continue

            manager = self._get_user(assignee.manager_id)
            if not manager:
                logger.warning("No manager for user %s, skipping escalation for task %s", assignee.id, task.id)
                continue

            days_overdue = max(0, (now - task.due_date).days)
            result = self.email.send_escalation(
                to=manager.email,
                manager_name=manager.name,
                employee_name=assignee.name,
                task_title=task.title,
                deadline=task.due_date,
                days_overdue=days_overdue,
                task_id=task.id,
                manager_id=manager.id,
            )
            if result["success"]:
                self._record_escalation(task, manager.id)
            processed.append(task.id)

        self.db.commit()
        return processed

    # ── Meeting summary ────────────────────────────────────────────────────────

    def send_meeting_summary_to_participants(self, meeting_id: str) -> dict:
        from app.models import Meeting

        meeting = self.db.get(Meeting, meeting_id)
        if not meeting:
            return {"success": False, "message": "Meeting not found"}

        summary_record: MeetingSummary | None = meeting.summary
        if not summary_record:
            return {"success": False, "message": "No summary available"}

        participants = self.db.scalars(
            select(MeetingParticipant).where(MeetingParticipant.meeting_id == meeting_id)
        ).all()

        emails = [p.participant_email for p in participants if p.participant_email]
        if not emails:
            return {"success": False, "message": "No participant emails found"}

        result = self.email.send_meeting_summary(
            to=emails,
            meeting_title=meeting.title,
            summary=summary_record.executive_summary,
            action_items=summary_record.action_items or [],
            decisions=summary_record.decisions or [],
            deadlines=[],
            meeting_id=meeting_id,
        )
        return result

    # ── Stop reminders when task completed ────────────────────────────────────

    def disable_reminders(self, task_id: str) -> None:
        task = self.db.get(Task, task_id)
        if task:
            task.reminder_enabled = False
            self.db.flush()
