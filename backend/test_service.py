import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from app.services.employee_service import EmployeeService
from app.schemas.employee import EmployeeCreate
from app.database.session import SessionLocal

db = SessionLocal()
svc = EmployeeService(db)

OWNER_ID = "83006f88-4b52-4adc-9d6c-9a166516274c"

print("=== TEST LIST ===")
try:
    emps, total = svc.list(OWNER_ID)
    print(f"OK total={total}")
    for e in emps[:3]:
        print(f"  id={e.id} first={e.first_name} last={e.last_name} email={e.email}")
except Exception as ex:
    print(f"FAIL: {ex}")

print("\n=== TEST CREATE ===")
try:
    payload = EmployeeCreate(
        first_name="Diag",
        last_name="Test",
        email="diag.test.unique99@example.com",
        password="Test@1234",
        role="developer",
        status="active",
    )
    emp, pw = svc.create(payload, OWNER_ID)
    print(f"OK id={emp.id} emp_id={emp.employee_id} name={emp.name}")
    # cleanup
    db.delete(emp)
    db.commit()
    print("Cleaned up test employee")
except Exception as ex:
    db.rollback()
    print(f"FAIL: {ex}")

db.close()
