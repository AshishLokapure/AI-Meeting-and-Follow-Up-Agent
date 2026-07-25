from __future__ import annotations

import logging
import secrets
import string
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.employee import Employee
from app.models.enums import TaskStatus
from app.models.task import Task
from app.schemas.employee import (
    EMPLOYEE_ROLES,
    ROLE_KEYWORDS,
    EmployeeCreate,
    EmployeeOut,
    EmployeeProfile,
    EmployeeTaskStats,
    EmployeeUpdate,
)

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _generate_employee_id(db: Session) -> str:
    """Generate a unique EMP-XXXXX id."""
    for _ in range(20):
        candidate = "EMP-" + "".join(secrets.choice(string.digits) for _ in range(5))
        exists = db.scalar(select(Employee).where(Employee.employee_id == candidate))
        if not exists:
            return candidate
    raise RuntimeError("Could not generate unique employee_id")


def _generate_temp_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$"
    return "".join(secrets.choice(alphabet) for _ in range(length))


class EmployeeService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def create(self, payload: EmployeeCreate, added_by_id: str) -> tuple[Employee, str]:
        """Create employee. Returns (employee, plain_temp_password)."""
        emp_id = _generate_employee_id(self.db)
        plain_pw = payload.password
        emp = Employee(
            added_by_id=added_by_id,
            employee_id=emp_id,
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            email=payload.email.lower().strip(),
            phone=payload.phone,
            department=payload.department,
            designation=payload.designation,
            role=payload.role,
            status=payload.status,
            joining_date=payload.joining_date,
            manager_id=payload.manager_id,
            password_hash=hash_password(plain_pw),
        )
        self.db.add(emp)
        self.db.commit()
        self.db.refresh(emp)
        return emp, plain_pw

    def get_by_id(self, employee_id: str, added_by_id: str) -> Employee | None:
        return self.db.scalar(
            select(Employee).where(
                Employee.id == employee_id,
                Employee.added_by_id == added_by_id,
            )
        )

    def update(self, emp: Employee, payload: EmployeeUpdate) -> Employee:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(emp, field, value)
        self.db.commit()
        self.db.refresh(emp)
        return emp

    def delete(self, emp: Employee) -> None:
        self.db.delete(emp)
        self.db.commit()

    def list(
        self,
        added_by_id: str,
        *,
        q: str | None = None,
        department: str | None = None,
        role: str | None = None,
        status: str | None = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Employee], int]:
        stmt = select(Employee).where(Employee.added_by_id == added_by_id)

        if q:
            like = f"%{q.lower()}%"
            stmt = stmt.where(
                func.lower(Employee.first_name).like(like)
                | func.lower(Employee.last_name).like(like)
                | func.lower(Employee.email).like(like)
                | func.lower(Employee.employee_id).like(like)
            )
        if department:
            stmt = stmt.where(func.lower(Employee.department) == department.lower())
        if role:
            stmt = stmt.where(Employee.role == role)
        if status:
            stmt = stmt.where(Employee.status == status)

        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

        sort_col = {
            "name": Employee.first_name,
            "email": Employee.email,
            "department": Employee.department,
            "role": Employee.role,
            "status": Employee.status,
            "joining_date": Employee.joining_date,
            "created_at": Employee.created_at,
        }.get(sort_by, Employee.created_at)

        if sort_dir == "asc":
            stmt = stmt.order_by(sort_col.asc())
        else:
            stmt = stmt.order_by(sort_col.desc())

        offset = (page - 1) * page_size
        employees = list(self.db.scalars(stmt.offset(offset).limit(page_size)).all())
        return employees, total

    def get_departments(self, added_by_id: str) -> list[str]:
        rows = self.db.scalars(
            select(Employee.department)
            .where(Employee.added_by_id == added_by_id, Employee.department.is_not(None))
            .distinct()
            .order_by(Employee.department)
        ).all()
        return [r for r in rows if r]

    # ── Profile with task stats ────────────────────────────────────────────────

    def get_profile(self, employee_id: str, added_by_id: str) -> EmployeeProfile | None:
        emp = self.get_by_id(employee_id, added_by_id)
        if not emp:
            return None

        # Task stats — tasks where extracted_metadata->matched_employee_id == emp.id
        from sqlalchemy import cast, String as SAString
        from sqlalchemy.dialects.postgresql import JSONB

        tasks = self.db.scalars(
            select(Task).where(
                Task.extracted_metadata["matched_employee_id"].astext == emp.id
            )
        ).all()

        stats = EmployeeTaskStats(
            total=len(tasks),
            pending=sum(1 for t in tasks if t.status == TaskStatus.pending.value),
            in_progress=sum(1 for t in tasks if t.status == TaskStatus.in_progress.value),
            completed=sum(1 for t in tasks if t.status == TaskStatus.completed.value),
            overdue=sum(1 for t in tasks if t.status == TaskStatus.overdue.value),
        )

        recent = [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "meeting_id": t.meeting_id,
            }
            for t in sorted(tasks, key=lambda x: x.created_at, reverse=True)[:5]
        ]

        manager_out = None
        if emp.manager:
            from app.schemas.employee import ManagerBrief
            manager_out = ManagerBrief(
                id=emp.manager.id,
                first_name=emp.manager.first_name,
                last_name=emp.manager.last_name,
                email=emp.manager.email,
                designation=emp.manager.designation,
            )

        profile = EmployeeProfile(
            id=emp.id,
            employee_id=emp.employee_id,
            first_name=emp.first_name,
            last_name=emp.last_name,
            email=emp.email,
            phone=emp.phone,
            department=emp.department,
            designation=emp.designation,
            role=emp.role,
            status=emp.status,
            joining_date=emp.joining_date,
            profile_photo=emp.profile_photo,
            manager_id=emp.manager_id,
            created_at=emp.created_at,
            updated_at=emp.updated_at,
            name=emp.name,
            manager=manager_out,
            task_stats=stats,
            recent_tasks=recent,
        )
        return profile

    # ── Role-based intelligent assignment ─────────────────────────────────────

    def find_best_assignee(
        self,
        task_title: str,
        task_description: str,
        owner_name: str | None,
        added_by_id: str,
    ) -> Employee | None:
        """
        Assignment priority:
        1. Exact name match from transcript
        2. Partial name match
        3. Role keyword match (task title/description → role → least-loaded employee)
        4. Least-loaded active employee (round-robin fallback)
        """
        active_employees = list(
            self.db.scalars(
                select(Employee).where(
                    Employee.added_by_id == added_by_id,
                    Employee.status == "active",
                )
            ).all()
        )
        if not active_employees:
            return None

        # 1 & 2 — name matching
        if owner_name:
            lower_owner = owner_name.lower().strip()
            emp_by_name = {e.name.lower(): e for e in active_employees}
            if lower_owner in emp_by_name:
                return emp_by_name[lower_owner]
            for emp_name, emp in emp_by_name.items():
                if lower_owner in emp_name or emp_name in lower_owner:
                    return emp

        # 3 — role keyword matching
        combined_text = f"{task_title} {task_description or ''}".lower()
        matched_role: str | None = None
        best_score = 0
        for role, keywords in ROLE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in combined_text)
            if score > best_score:
                best_score = score
                matched_role = role

        if matched_role:
            role_employees = [e for e in active_employees if e.role == matched_role]
            if role_employees:
                return self._least_loaded(role_employees)

        # 4 — least-loaded fallback
        return self._least_loaded(active_employees)

    def _least_loaded(self, employees: list[Employee]) -> Employee:
        """Return the employee with the fewest pending/in-progress tasks."""
        def workload(emp: Employee) -> int:
            return self.db.scalar(
                select(func.count(Task.id)).where(
                    Task.extracted_metadata["matched_employee_id"].astext == emp.id,
                    Task.status.in_([TaskStatus.pending.value, TaskStatus.in_progress.value]),
                )
            ) or 0

        return min(employees, key=workload)
