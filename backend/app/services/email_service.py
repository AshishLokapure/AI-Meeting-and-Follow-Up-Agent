from __future__ import annotations

import logging
import re
from email.message import EmailMessage
from pathlib import Path
from smtplib import SMTP, SMTPException
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape

from app.core.settings import get_settings
from app.database.session import SessionLocal
from app.models.notification_log import NotificationLog

logger = logging.getLogger(__name__)
settings = get_settings()

_TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates" / "emails"
_jinja_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)


def _render(template_name: str, context: dict[str, Any]) -> tuple[str, str]:
    """Return (html_body, plain_text_body)."""
    try:
        html = _jinja_env.get_template(f"{template_name}.html").render(**context)
    except TemplateNotFound:
        logger.warning("Template %s not found, falling back to plain text", template_name)
        html = "<p>" + context.get("body", "") + "</p>"
    plain = re.sub(r"<[^>]+>", "", html).strip()
    return html, plain


def _build_message(
    to: str | list[str],
    subject: str,
    html: str,
    plain: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: list[tuple[str, bytes, str]] | None = None,
) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{settings.mail_from_name} <{settings.mail_from}>"
    msg["To"] = ", ".join([to] if isinstance(to, str) else to)
    if cc:
        msg["Cc"] = ", ".join(cc)
    if bcc:
        msg["Bcc"] = ", ".join(bcc)
    msg.set_content(plain)
    msg.add_alternative(html, subtype="html")
    for filename, content, _ in attachments or []:
        msg.add_attachment(content, maintype="application", subtype="octet-stream", filename=filename)
    return msg


def _smtp_send(msg: EmailMessage) -> tuple[bool, str]:
    """Send via SMTP with STARTTLS. Returns (success, response_text)."""
    try:
        with SMTP(settings.mail_host, settings.mail_port, timeout=15) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(settings.mail_username, settings.mail_password)
            smtp.send_message(msg)
        return True, "sent"
    except SMTPException as exc:
        logger.error("SMTP error: %s", exc)
        return False, str(exc)
    except Exception as exc:
        logger.exception("Unexpected SMTP failure")
        return False, str(exc)


def _persist_log(
    *,
    recipient_email: str,
    subject: str,
    html: str,
    template_name: str,
    delivery_status: str,
    smtp_response: str,
    user_id: str | None,
    task_id: str | None,
    retry_count: int = 0,
) -> None:
    db = SessionLocal()
    try:
        log = NotificationLog(
            user_id=user_id,
            task_id=task_id,
            subject=subject,
            body=html,
            template_name=template_name,
            recipient_email=recipient_email,
            delivery_status=delivery_status,
            smtp_response=smtp_response,
            retry_count=retry_count,
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to persist notification log")
    finally:
        db.close()


class EmailService:
    """
    Central SMTP email service.

    All public methods are synchronous and designed to be called from
    Celery tasks so the FastAPI request thread is never blocked.
    """

    def send_email(
        self,
        to: str | list[str],
        subject: str,
        template_name: str,
        context: dict[str, Any],
        *,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        attachments: list[tuple[str, bytes, str]] | None = None,
        user_id: str | None = None,
        task_id: str | None = None,
        retry_count: int = 0,
    ) -> dict[str, Any]:
        html, plain = _render(template_name, context)
        msg = _build_message(to, subject, html, plain, cc=cc, bcc=bcc, attachments=attachments)
        success, response = _smtp_send(msg)
        status = "sent" if success else "failed"
        recipient = to if isinstance(to, str) else to[0]
        _persist_log(
            recipient_email=recipient,
            subject=subject,
            html=html,
            template_name=template_name,
            delivery_status=status,
            smtp_response=response,
            user_id=user_id,
            task_id=task_id,
            retry_count=retry_count,
        )
        logger.info("Email [%s] to=%s status=%s", template_name, recipient, status)
        return {"success": success, "status": status, "smtp_response": response, "to": to, "subject": subject}

    # ── Auth emails ────────────────────────────────────────────────────────────

    def send_welcome_email(self, to: str, user_name: str, user_id: str | None = None) -> dict[str, Any]:
        return self.send_email(
            to, "Welcome to AI Meeting Agent 🎉", "welcome",
            {"user_name": user_name, "app_name": settings.app_name},
            user_id=user_id,
        )

    def send_verification_email(
        self, to: str, user_name: str, verification_url: str, user_id: str | None = None
    ) -> dict[str, Any]:
        return self.send_email(
            to, "Verify your email address", "verify_email",
            {"user_name": user_name, "verification_url": verification_url, "app_name": settings.app_name},
            user_id=user_id,
        )

    def send_password_reset_email(
        self, to: str, user_name: str, reset_url: str, user_id: str | None = None
    ) -> dict[str, Any]:
        return self.send_email(
            to, "Reset your password", "forgot_password",
            {"user_name": user_name, "reset_url": reset_url, "app_name": settings.app_name},
            user_id=user_id,
        )

    def send_password_changed_email(self, to: str, user_name: str, user_id: str | None = None) -> dict[str, Any]:
        return self.send_email(
            to, "Your password was changed", "password_changed",
            {"user_name": user_name, "app_name": settings.app_name},
            user_id=user_id,
        )

    # ── Task emails ────────────────────────────────────────────────────────────

    def send_task_assignment(
        self,
        to: str,
        assignee_name: str,
        assigner_name: str,
        task_title: str,
        task_description: str,
        deadline: Any,
        priority: str,
        task_id: str | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        return self.send_email(
            to, f"New task assigned: {task_title}", "task_assignment",
            {
                "assignee_name": assignee_name,
                "assigner_name": assigner_name,
                "task_title": task_title,
                "task_description": task_description or "No description provided.",
                "deadline": deadline,
                "priority": priority,
                "app_name": settings.app_name,
            },
            user_id=user_id,
            task_id=task_id,
        )

    def send_daily_reminder(
        self,
        to: str,
        assignee_name: str,
        task_title: str,
        task_description: str,
        deadline: Any,
        priority: str,
        task_id: str | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        return self.send_email(
            to, f"Daily reminder: {task_title}", "daily_reminder",
            {
                "assignee_name": assignee_name,
                "task_title": task_title,
                "task_description": task_description or "",
                "deadline": deadline,
                "priority": priority,
                "app_name": settings.app_name,
            },
            user_id=user_id,
            task_id=task_id,
        )

    def send_deadline_reminder(
        self,
        to: str,
        assignee_name: str,
        task_title: str,
        task_description: str,
        deadline: Any,
        hours_remaining: int,
        task_id: str | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        return self.send_email(
            to, f"⚠️ Deadline in {hours_remaining}h: {task_title}", "deadline_reminder",
            {
                "assignee_name": assignee_name,
                "task_title": task_title,
                "task_description": task_description or "",
                "deadline": deadline,
                "hours_remaining": hours_remaining,
                "app_name": settings.app_name,
            },
            user_id=user_id,
            task_id=task_id,
        )

    def send_escalation(
        self,
        to: str,
        manager_name: str,
        employee_name: str,
        task_title: str,
        deadline: Any,
        days_overdue: int,
        task_id: str | None = None,
        manager_id: str | None = None,
    ) -> dict[str, Any]:
        return self.send_email(
            to, f"🚨 Escalation: Overdue task — {task_title}", "escalation",
            {
                "manager_name": manager_name,
                "employee_name": employee_name,
                "task_title": task_title,
                "deadline": deadline,
                "days_overdue": days_overdue,
                "app_name": settings.app_name,
            },
            user_id=manager_id,
            task_id=task_id,
        )

    def send_meeting_summary(
        self,
        to: str | list[str],
        meeting_title: str,
        summary: str,
        action_items: list[str],
        decisions: list[str],
        deadlines: list[str],
        meeting_id: str | None = None,
    ) -> dict[str, Any]:
        return self.send_email(
            to, f"Meeting Summary: {meeting_title}", "meeting_summary",
            {
                "meeting_title": meeting_title,
                "summary": summary,
                "action_items": action_items,
                "decisions": decisions,
                "deadlines": deadlines,
                "app_name": settings.app_name,
            },
        )

    def send_employee_welcome(
        self,
        to: str,
        employee_name: str,
        employee_id: str,
        temp_password: str,
        department: str,
        role: str,
        login_url: str,
        reset_url: str,
        org_name: str = "Your Organization",
        user_id: str | None = None,
    ) -> dict[str, Any]:
        return self.send_email(
            to,
            f"Welcome to {org_name} — Your Login Credentials",
            "employee_welcome",
            {
                "employee_name": employee_name,
                "employee_id": employee_id,
                "email": to,
                "temp_password": temp_password,
                "department": department or "—",
                "role": role.replace("_", " ").title(),
                "login_url": login_url,
                "reset_url": reset_url,
                "org_name": org_name,
                "app_name": settings.app_name,
            },
            user_id=user_id,
        )

    def send_custom_email(
        self,
        to: str,
        subject: str,
        body: str,
        user_id: str | None = None,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        return self.send_email(
            to, subject, "custom_notification",
            {"subject": subject, "body": body, "app_name": settings.app_name},
            user_id=user_id,
            task_id=task_id,
        )
