"""
Celery Beat periodic task schedule.

Import this module in celery_app.py to register the beat schedule.
"""
from celery.schedules import crontab

BEAT_SCHEDULE: dict = {
    # Daily reminders — every day at 08:00 UTC
    "daily-task-reminders": {
        "task": "scheduler.daily_reminders",
        "schedule": crontab(hour=8, minute=0),
    },
    # Deadline reminders — every hour (catches 24-hour windows)
    "deadline-reminders-hourly": {
        "task": "scheduler.deadline_reminders",
        "schedule": crontab(minute=0),
    },
    # Escalations — every day at 09:00 UTC
    "daily-escalations": {
        "task": "scheduler.escalations",
        "schedule": crontab(hour=9, minute=0),
    },
}
