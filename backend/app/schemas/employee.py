from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ── Role / Status constants exposed to frontend ────────────────────────────────

EMPLOYEE_ROLES = [
    "admin", "manager", "developer", "ai_engineer", "ml_engineer",
    "backend_developer", "frontend_developer", "qa_engineer",
    "hr", "marketing", "sales", "devops", "custom",
]

EMPLOYEE_STATUSES = ["active", "inactive", "on_leave"]

# Maps role → keywords used for intelligent task assignment
ROLE_KEYWORDS: dict[str, list[str]] = {
    "frontend_developer": ["ui", "frontend", "design", "css", "react", "interface", "component"],
    "backend_developer": ["api", "backend", "server", "database", "endpoint", "service"],
    "ai_engineer": ["ai", "model", "llm", "gpt", "openai", "inference", "prompt"],
    "ml_engineer": ["ml", "train", "machine learning", "dataset", "pipeline", "feature"],
    "qa_engineer": ["test", "qa", "quality", "bug", "testing", "automation"],
    "devops": ["deploy", "docker", "ci", "cd", "kubernetes", "infrastructure", "pipeline"],
    "hr": ["hr", "hire", "onboard", "recruit", "policy"],
    "marketing": ["marketing", "campaign", "social", "content", "seo"],
    "sales": ["sales", "client", "deal", "proposal", "crm"],
    "manager": ["review", "approve", "plan", "coordinate", "manage"],
}


# ── Request schemas ────────────────────────────────────────────────────────────

class EmployeeCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=75)
    last_name: str = Field(min_length=1, max_length=75)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=30)
    department: Optional[str] = Field(default=None, max_length=100)
    designation: Optional[str] = Field(default=None, max_length=100)
    role: str = Field(default="developer")
    status: str = Field(default="active")
    joining_date: Optional[date] = None
    manager_id: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in EMPLOYEE_ROLES:
            raise ValueError(f"role must be one of {EMPLOYEE_ROLES}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in EMPLOYEE_STATUSES:
            raise ValueError(f"status must be one of {EMPLOYEE_STATUSES}")
        return v


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = Field(default=None, min_length=1, max_length=75)
    last_name: Optional[str] = Field(default=None, min_length=1, max_length=75)
    phone: Optional[str] = Field(default=None, max_length=30)
    department: Optional[str] = Field(default=None, max_length=100)
    designation: Optional[str] = Field(default=None, max_length=100)
    role: Optional[str] = None
    status: Optional[str] = None
    joining_date: Optional[date] = None
    manager_id: Optional[str] = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str | None) -> str | None:
        if v is not None and v not in EMPLOYEE_ROLES:
            raise ValueError(f"role must be one of {EMPLOYEE_ROLES}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is not None and v not in EMPLOYEE_STATUSES:
            raise ValueError(f"status must be one of {EMPLOYEE_STATUSES}")
        return v


# ── Response schemas ───────────────────────────────────────────────────────────

class ManagerBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    first_name: str
    last_name: str
    email: str
    designation: Optional[str] = None


class EmployeeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    employee_id: Optional[str] = None
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    role: str
    status: str
    joining_date: Optional[date] = None
    profile_photo: Optional[str] = None
    manager_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Computed
    name: str = ""

    @classmethod
    def from_orm_with_name(cls, emp: object) -> "EmployeeOut":
        obj = cls.model_validate(emp)
        obj.name = getattr(emp, "name", "")
        return obj


class EmployeeTaskStats(BaseModel):
    total: int = 0
    pending: int = 0
    in_progress: int = 0
    completed: int = 0
    overdue: int = 0


class EmployeeProfile(EmployeeOut):
    manager: Optional[ManagerBrief] = None
    task_stats: EmployeeTaskStats = EmployeeTaskStats()
    recent_tasks: list[dict] = []


class EmployeeListResponse(BaseModel):
    employees: list[EmployeeOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class EmployeeMetaResponse(BaseModel):
    roles: list[str]
    statuses: list[str]
    departments: list[str]
