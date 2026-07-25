"""
Celery tasks for email delivery.

All FastAPI endpoints enqueue these tasks instead of sending emails
synchronously, so the HTTP response is never blocked by SMTP.
"""
from __future__ import annotations

from celery.utils.log import get_task_logger

from app.core.settings import get_settings
from app.database.session import SessionLocal
from app.services.email_service import EmailService
from app.services.notification_service import NotificationService
from app.workers.celery_app import celery_app

logger = get_task_logger(__name__)
settings = get_settings()

_MAX_RETRIES = settings.email_max_retries
_RETRY_BACKOFF = settings.email_retry_backoff  # seconds


# ── Auth email tasks ───────────────────────────────────────────────────────────

@celery_app.task(
    name="email.send_welcome",
    bind=True,
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_BACKOFF,
)
def send_welcome_email(self, to: str, user_name: str, user_id: str | None = None) -> dict:
    try:
        return EmailService().send_welcome_email(to, user_name, user_id=user_id)
    except Exception as exc:
        logger.error("send_welcome_email failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(
    name="email.send_verification",
    bind=True,
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_BACKOFF,
)
def send_verification_email(
    self, to: str, user_name: str, verification_url: str, user_id: str | None = None
) -> dict:
    try:
        return EmailService().send_verification_email(to, user_name, verification_url, user_id=user_id)
    except Exception as exc:
        logger.error("send_verification_email failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(
    name="email.send_password_reset",
    bind=True,
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_BACKOFF,
)
def send_password_reset_email(
    self, to: str, user_name: str, reset_url: str, user_id: str | None = None
) -> dict:
    try:
        return EmailService().send_password_reset_email(to, user_name, reset_url, user_id=user_id)
    except Exception as exc:
        logger.error("send_password_reset_email failed: %s", exc)
        raise self.retry(exc=exc)


@celery_app.task(
    name="email.send_password_changed",
    bind=True,
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_BACKOFF,
)
def send_password_changed_email(self, to: str, user_name: str, user_id: str | None = None) -> dict:
    try:
        return EmailService().send_password_changed_email(to, user_name, user_id=user_id)
    except Exception as exc:
        logger.error("send_password_changed_email failed: %s", exc)
        raise self.retry(exc=exc)


# ── Task email tasks ───────────────────────────────────────────────────────────

@celery_app.task(
    name="email.send_task_assignment",
    bind=True,
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_BACKOFF,
)
def send_task_assignment_email(self, task_id: str) -> dict:
    db = SessionLocal()
    try:
        result = NotificationService(db).notify_task_assigned(db.get(__import__("app.models", fromlist=["Task"]).Task, task_id))
        return result
    except Exception as exc:
        logger.error("send_task_assignment_email failed for task %s: %s", task_id, exc)
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(
    name="email.send_custom",
    bind=True,
    max_retries=_MAX_RETRIES,
    default_retry_delay=_RETRY_BACKOFF,
)
def send_custom_email(
    self, to: str, subject: str, body: str, user_id: str | None = None, task_id: str | None = None
) -> dict:
    try:
        return EmailService().send_custom_email(to, subject, body, user_id=user_id, task_id=task_id)
    except Exception as exc:
        logger.error("send_custom_email failed: %s", exc)
        raise self.retry(exc=exc)


# ── Scheduled / periodic tasks ─────────────────────────────────────────────────

@celery_app.task(name="scheduler.daily_reminders")
def run_daily_reminders() -> dict:
    """Celery Beat triggers this every 24 hours."""
    db = SessionLocal()
    try:
        processed = NotificationService(db).send_daily_reminders()
        return {"processed": len(processed), "task_ids": processed}
    except Exception:
        logger.exception("run_daily_reminders failed")
        raise
    finally:
        db.close()


@celery_app.task(name="scheduler.deadline_reminders")
def run_deadline_reminders() -> dict:
    """Celery Beat triggers this every hour to catch 24-hour deadline windows."""
    db = SessionLocal()
    try:
        processed = NotificationService(db).send_deadline_reminders()
        return {"processed": len(processed), "task_ids": processed}
    except Exception:
        logger.exception("run_deadline_reminders failed")
        raise
    finally:
        db.close()


@celery_app.task(name="scheduler.escalations")
def run_escalations() -> dict:
    """Celery Beat triggers this every 24 hours for overdue tasks."""
    db = SessionLocal()
    try:
        processed = NotificationService(db).send_escalations()
        return {"processed": len(processed), "task_ids": processed}
    except Exception:
        logger.exception("run_escalations failed")
        raise
    finally:
        db.close()


@celery_app.task(name="email.send_meeting_summary", bind=True, max_retries=_MAX_RETRIES)
def send_meeting_summary_email(self, meeting_id: str) -> dict:
    db = SessionLocal()
    try:
        return NotificationService(db).send_meeting_summary_to_participants(meeting_id)
    except Exception as exc:
        logger.error("send_meeting_summary_email failed for meeting %s: %s", meeting_id, exc)
        raise self.retry(exc=exc)
    finally:
        db.close()
