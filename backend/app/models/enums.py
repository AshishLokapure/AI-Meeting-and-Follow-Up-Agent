from enum import Enum


class MeetingStatus(str, Enum):
    uploaded = "uploaded"
    queued = "queued"
    processing = "processing"
    transcribed = "transcribed"
    summarized = "summarized"
    analyzed = "analyzed"
    archived = "archived"


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    blocked = "blocked"
    completed = "completed"
    overdue = "overdue"
    cancelled = "cancelled"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class NotificationChannel(str, Enum):
    in_app = "in_app"
    email = "email"
    slack = "slack"
    teams = "teams"


class NotificationStatus(str, Enum):
    queued = "queued"
    sent = "sent"
    failed = "failed"
    read = "read"


class ReminderStatus(str, Enum):
    scheduled = "scheduled"
    sent = "sent"
    failed = "failed"
    skipped = "skipped"


class LogLevel(str, Enum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


class BackgroundJobStatus(str, Enum):
    queued = "queued"
    started = "started"
    succeeded = "succeeded"
    failed = "failed"


class EmployeeStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    on_leave = "on_leave"


class EmployeeRole(str, Enum):
    admin = "admin"
    manager = "manager"
    developer = "developer"
    ai_engineer = "ai_engineer"
    ml_engineer = "ml_engineer"
    backend_developer = "backend_developer"
    frontend_developer = "frontend_developer"
    qa_engineer = "qa_engineer"
    hr = "hr"
    marketing = "marketing"
    sales = "sales"
    devops = "devops"
    custom = "custom"
