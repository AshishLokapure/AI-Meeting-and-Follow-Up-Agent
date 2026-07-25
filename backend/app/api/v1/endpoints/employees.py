from __future__ import annotations

import math

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_verified_user
from app.core.settings import get_settings
from app.database import get_db
from app.models.employee import Employee
from app.schemas.employee import (
    EMPLOYEE_ROLES,
    EMPLOYEE_STATUSES,
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeMetaResponse,
    EmployeeOut,
    EmployeeProfile,
    EmployeeUpdate,
)
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["employees"])


def _out(emp: Employee) -> EmployeeOut:
    return EmployeeOut.from_orm_with_name(emp)


# ── Meta ───────────────────────────────────────────────────────────────────────

@router.get("/meta", response_model=EmployeeMetaResponse)
def get_meta(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> EmployeeMetaResponse:
    svc = EmployeeService(db)
    return EmployeeMetaResponse(
        roles=EMPLOYEE_ROLES,
        statuses=EMPLOYEE_STATUSES,
        departments=svc.get_departments(current_user.id),
    )


# ── List / Search ──────────────────────────────────────────────────────────────

@router.get("", response_model=EmployeeListResponse)
def list_employees(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
    q: str | None = Query(default=None, max_length=200),
    department: str | None = Query(default=None),
    role: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    sort_by: str = Query(default="created_at"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> EmployeeListResponse:
    svc = EmployeeService(db)
    employees, total = svc.list(
        current_user.id,
        q=q,
        department=department,
        role=role,
        status=status_filter,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )
    return EmployeeListResponse(
        employees=[_out(e) for e in employees],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, math.ceil(total / page_size)),
    )


# ── Create ─────────────────────────────────────────────────────────────────────

@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def create_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> EmployeeOut:
    # Unique email check
    if db.scalar(select(Employee).where(Employee.email == payload.email.lower())):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # Unique phone check
    if payload.phone and db.scalar(select(Employee).where(Employee.phone == payload.phone)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone number already registered")

    svc = EmployeeService(db)
    emp, plain_pw = svc.create(payload, current_user.id)

    # Send welcome email with credentials (non-blocking — fire and forget)
    try:
        settings = get_settings()
        from app.services.email_service import EmailService
        EmailService().send_employee_welcome(
            to=emp.email,
            employee_name=emp.name,
            employee_id=emp.employee_id or "",
            temp_password=plain_pw,
            department=emp.department or "",
            role=emp.role,
            login_url=f"{settings.frontend_url}/login",
            reset_url=f"{settings.frontend_url}/forgot-password",
            org_name=current_user.name,
        )
    except Exception:
        pass  # Email failure must not block employee creation

    return _out(emp)


# ── Get single ─────────────────────────────────────────────────────────────────

@router.get("/{employee_id}/profile", response_model=EmployeeProfile)
def get_employee_profile(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> EmployeeProfile:
    svc = EmployeeService(db)
    profile = svc.get_profile(employee_id, current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return profile


@router.get("/{employee_id}", response_model=EmployeeOut)
def get_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> EmployeeOut:
    svc = EmployeeService(db)
    emp = svc.get_by_id(employee_id, current_user.id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    return _out(emp)


# ── Update ─────────────────────────────────────────────────────────────────────

@router.put("/{employee_id}", response_model=EmployeeOut)
@router.patch("/{employee_id}", response_model=EmployeeOut)
def update_employee(
    employee_id: str,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> EmployeeOut:
    svc = EmployeeService(db)
    emp = svc.get_by_id(employee_id, current_user.id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    emp = svc.update(emp, payload)
    return _out(emp)


# ── Delete ─────────────────────────────────────────────────────────────────────

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> None:
    svc = EmployeeService(db)
    emp = svc.get_by_id(employee_id, current_user.id)
    if not emp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    svc.delete(emp)
