from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_verified_user, require_roles
from app.database import get_db
from app.models.employee import Employee

router = APIRouter(prefix="/employees", tags=["employees"])


# ── Schemas ────────────────────────────────────────────────────────────────────

class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    department: str | None = None
    designation: str | None = None


class EmployeeUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    department: str | None = None
    designation: str | None = None
    is_active: bool | None = None


class EmployeeOut(BaseModel):
    id: str
    name: str
    email: str
    phone: str | None
    department: str | None
    designation: str | None
    is_active: bool
    created_at: str

    model_config = {"from_attributes": True}


def _to_out(e: Employee) -> EmployeeOut:
    return EmployeeOut(
        id=e.id,
        name=e.name,
        email=e.email,
        phone=e.phone,
        department=e.department,
        designation=e.designation,
        is_active=e.is_active,
        created_at=e.created_at.isoformat(),
    )


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.get("", response_model=list[EmployeeOut])
def list_employees(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> list[EmployeeOut]:
    """All employees added by the current admin/manager."""
    employees = db.scalars(
        select(Employee)
        .where(Employee.added_by_id == current_user.id)
        .order_by(Employee.name)
    ).all()
    return [_to_out(e) for e in employees]


@router.post("", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
def add_employee(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> EmployeeOut:
    """Add a new employee. Email must be unique."""
    existing = db.scalar(select(Employee).where(Employee.email == payload.email.lower()))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Employee with this email already exists")

    emp = Employee(
        added_by_id=current_user.id,
        name=payload.name.strip(),
        email=payload.email.lower(),
        phone=payload.phone,
        department=payload.department,
        designation=payload.designation,
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return _to_out(emp)


@router.patch("/{employee_id}", response_model=EmployeeOut)
def update_employee(
    employee_id: str,
    payload: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> EmployeeOut:
    emp = db.get(Employee, employee_id)
    if not emp or emp.added_by_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(emp, field, value)

    db.commit()
    db.refresh(emp)
    return _to_out(emp)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_verified_user),
) -> None:
    emp = db.get(Employee, employee_id)
    if not emp or emp.added_by_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    db.delete(emp)
    db.commit()
