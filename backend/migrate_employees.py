"""
Run this once to migrate the employees table from the old schema to the new one.

    cd backend
    python migrate_employees.py
"""
import psycopg2

DSN = "postgresql://postgres:Ashish19@localhost:5432/AI_Meeting_Flow"

STEPS = [
    # 1. Add new columns (all nullable so existing rows don't break)
    "ALTER TABLE employees ADD COLUMN IF NOT EXISTS manager_id VARCHAR(36) REFERENCES employees(id) ON DELETE SET NULL",
    "ALTER TABLE employees ADD COLUMN IF NOT EXISTS employee_id VARCHAR(50) UNIQUE",
    "ALTER TABLE employees ADD COLUMN IF NOT EXISTS first_name VARCHAR(75)",
    "ALTER TABLE employees ADD COLUMN IF NOT EXISTS last_name VARCHAR(75)",
    "ALTER TABLE employees ADD COLUMN IF NOT EXISTS role VARCHAR(50) DEFAULT 'developer'",
    "ALTER TABLE employees ADD COLUMN IF NOT EXISTS profile_photo VARCHAR(500)",
    "ALTER TABLE employees ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255)",
    "ALTER TABLE employees ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active'",
    "ALTER TABLE employees ADD COLUMN IF NOT EXISTS joining_date DATE",
    "ALTER TABLE employees ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ",

    # 2. Back-fill first_name / last_name from the old `name` column
    """
    UPDATE employees
    SET
        first_name = SPLIT_PART(COALESCE(name, 'Unknown'), ' ', 1),
        last_name  = CASE
                        WHEN POSITION(' ' IN COALESCE(name, '')) > 0
                        THEN SUBSTRING(COALESCE(name, '') FROM POSITION(' ' IN COALESCE(name, '')) + 1)
                        ELSE ''
                     END
    WHERE first_name IS NULL
    """,

    # 3. Back-fill status from is_active
    "UPDATE employees SET status = CASE WHEN is_active THEN 'active' ELSE 'inactive' END WHERE status IS NULL OR status = ''",

    # 4. Make first_name / last_name / role / status NOT NULL now that they're filled
    "ALTER TABLE employees ALTER COLUMN first_name SET NOT NULL",
    "ALTER TABLE employees ALTER COLUMN last_name SET NOT NULL",
    "ALTER TABLE employees ALTER COLUMN role SET NOT NULL",
    "ALTER TABLE employees ALTER COLUMN status SET NOT NULL",

    # 5. Create index on manager_id
    "CREATE INDEX IF NOT EXISTS ix_employees_manager_id ON employees(manager_id)",
    "CREATE INDEX IF NOT EXISTS ix_employees_employee_id ON employees(employee_id)",

    # 6. Drop the old `name` column (no longer needed — kept as is_active for compat)
    # We keep is_active so existing seed data / foreign code doesn't break immediately.
    # The new model uses `status` instead.
]


def run():
    conn = psycopg2.connect(DSN)
    conn.autocommit = False
    cur = conn.cursor()
    try:
        for sql in STEPS:
            sql = sql.strip()
            if not sql:
                continue
            print(f"  -> {sql[:80]}...")
            cur.execute(sql)
        conn.commit()
        print("\nMigration complete.")
    except Exception as exc:
        conn.rollback()
        print(f"\nMigration FAILED: {exc}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    run()
