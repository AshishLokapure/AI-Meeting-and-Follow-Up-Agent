"""
seed_db.py — Run once to fix schema + populate demo data.

Usage (from backend/ folder):
    python seed_db.py
"""

import sys
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.chdir(Path(__file__).resolve().parent)

from sqlalchemy import text
from app.database.session import engine, SessionLocal
from app.database.base import Base
from app.core.security import hash_password

import app.models  # noqa: F401 — registers all models with Base.metadata
from app.models.enums import TaskPriority, TaskStatus, MeetingStatus


# ── helpers ───────────────────────────────────────────────────────────────────

def utcnow() -> datetime:
    return datetime.now(timezone.utc)


DEMO_PASSWORD = "Demo@1234"


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — ALTER existing tables (idempotent)
# ══════════════════════════════════════════════════════════════════════════════

MIGRATIONS = [
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS employee_id VARCHAR(50)",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS department VARCHAR(100)",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS designation VARCHAR(100)",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS manager_id VARCHAR(255) REFERENCES users(id) ON DELETE SET NULL",
    "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS assigned_by_id VARCHAR(255) REFERENCES users(id) ON DELETE SET NULL",
    "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS completion_date TIMESTAMPTZ",
    "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reminder_enabled BOOLEAN NOT NULL DEFAULT TRUE",
    "ALTER TABLE tasks ADD COLUMN IF NOT EXISTS reminder_interval_hours INTEGER NOT NULL DEFAULT 24",
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_indexes
            WHERE tablename='users' AND indexname='ix_users_employee_id'
        ) THEN
            CREATE UNIQUE INDEX ix_users_employee_id ON users(employee_id)
            WHERE employee_id IS NOT NULL;
        END IF;
    END$$;
    """,
]


def run_migrations() -> None:
    print("Running schema migrations...")
    with engine.begin() as conn:
        for sql in MIGRATIONS:
            try:
                conn.execute(text(sql.strip()))
                print(f"  OK: {sql.strip()[:72]}")
            except Exception as e:
                print(f"  SKIP: {str(e)[:80]}")
    print()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — CREATE new tables
# ══════════════════════════════════════════════════════════════════════════════

def create_tables() -> None:
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("  OK: all tables verified\n")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Seed
# ══════════════════════════════════════════════════════════════════════════════

DEMO_USERS = [
    {
        "name": "Ashish Lokapure",
        "email": "ashishlokapure19@gmail.com",
        "role": "admin",
        "employee_id": "EMP001",
        "department": "Engineering",
        "designation": "CTO",
        "manager_email": None,
    },
    {
        "name": "Priya Sharma",
        "email": "priya.sharma@demo.com",
        "role": "manager",
        "employee_id": "EMP002",
        "department": "Engineering",
        "designation": "Engineering Manager",
        "manager_email": "ashishlokapure19@gmail.com",
    },
    {
        "name": "Rahul Mehta",
        "email": "rahul.mehta@demo.com",
        "role": "member",
        "employee_id": "EMP003",
        "department": "Engineering",
        "designation": "Senior Developer",
        "manager_email": "priya.sharma@demo.com",
    },
    {
        "name": "Sneha Patil",
        "email": "sneha.patil@demo.com",
        "role": "member",
        "employee_id": "EMP004",
        "department": "Product",
        "designation": "Product Manager",
        "manager_email": "priya.sharma@demo.com",
    },
    {
        "name": "Arjun Nair",
        "email": "arjun.nair@demo.com",
        "role": "member",
        "employee_id": "EMP005",
        "department": "Design",
        "designation": "UI/UX Designer",
        "manager_email": "priya.sharma@demo.com",
    },
]


def seed_users(db) -> dict:
    """Upsert users by email. Returns email->real_db_id map."""
    print("  -> Users")
    pw_hash = hash_password(DEMO_PASSWORD)
    email_to_id: dict[str, str] = {}

    # First pass: upsert each user (no manager_id yet)
    for u in DEMO_USERS:
        row = db.execute(
            text("SELECT id FROM users WHERE email = :e"),
            {"e": u["email"]}
        ).first()

        if row:
            real_id = row[0]
            db.execute(text("""
                UPDATE users SET
                    name        = :name,
                    role        = :role,
                    employee_id = :eid,
                    department  = :dept,
                    designation = :desig,
                    email_verified      = TRUE,
                    email_verified_at   = NOW(),
                    is_active           = TRUE
                WHERE id = :id
            """), {
                "name": u["name"], "role": u["role"],
                "eid": u["employee_id"], "dept": u["department"],
                "desig": u["designation"], "id": real_id,
            })
            print(f"     updated : {u['email']} [{u['role']}]")
        else:
            real_id = str(uuid4())
            db.execute(text("""
                INSERT INTO users
                    (id, name, email, password_hash, role, is_active,
                     email_verified, email_verified_at,
                     employee_id, department, designation)
                VALUES
                    (:id, :name, :email, :pw, :role, TRUE,
                     TRUE, NOW(),
                     :eid, :dept, :desig)
            """), {
                "id": real_id, "name": u["name"], "email": u["email"],
                "pw": pw_hash, "role": u["role"],
                "eid": u["employee_id"], "dept": u["department"],
                "desig": u["designation"],
            })
            print(f"     created : {u['email']} [{u['role']}]")

        email_to_id[u["email"]] = real_id

    db.flush()

    # Second pass: set manager_id now that all IDs are known
    for u in DEMO_USERS:
        if u["manager_email"]:
            mgr_id = email_to_id.get(u["manager_email"])
            if mgr_id:
                db.execute(text(
                    "UPDATE users SET manager_id = :m WHERE id = :i"
                ), {"m": mgr_id, "i": email_to_id[u["email"]]})

    db.flush()
    return email_to_id


def seed_meetings(db, uid: dict) -> dict:
    """Insert meetings. Returns demo_key->real_db_id map."""
    print("  -> Meetings")
    meetings = [
        {
            "key": "mtg-001",
            "owner": "ashishlokapure19@gmail.com",
            "title": "Q1 Product Roadmap Planning",
            "agenda": "Review Q1 goals, assign tasks, set deadlines.",
            "meeting_date": (utcnow() - timedelta(days=3)).date(),
            "status": MeetingStatus.analyzed.value,
            "duration_minutes": 60,
        },
        {
            "key": "mtg-002",
            "owner": "priya.sharma@demo.com",
            "title": "Sprint 12 Kickoff",
            "agenda": "Sprint planning, story points, assignments.",
            "meeting_date": (utcnow() - timedelta(days=1)).date(),
            "status": MeetingStatus.analyzed.value,
            "duration_minutes": 45,
        },
        {
            "key": "mtg-003",
            "owner": "ashishlokapure19@gmail.com",
            "title": "AI Feature Demo Review",
            "agenda": "Demo the new AI meeting agent features.",
            "meeting_date": utcnow().date(),
            "status": MeetingStatus.summarized.value,
            "duration_minutes": 30,
        },
    ]

    key_to_id: dict[str, str] = {}
    for m in meetings:
        row = db.execute(
            text("SELECT id FROM meetings WHERE title = :t AND owner_id = :o"),
            {"t": m["title"], "o": uid[m["owner"]]}
        ).first()
        if row:
            key_to_id[m["key"]] = row[0]
            print(f"     skip    : {m['title']}")
            continue
        mid = str(uuid4())
        db.execute(text("""
            INSERT INTO meetings
                (id, owner_id, title, agenda, meeting_date, status, duration_minutes)
            VALUES
                (:id, :owner, :title, :agenda, :date, :status, :dur)
        """), {
            "id": mid, "owner": uid[m["owner"]], "title": m["title"],
            "agenda": m["agenda"], "date": m["meeting_date"],
            "status": m["status"], "dur": m["duration_minutes"],
        })
        key_to_id[m["key"]] = mid
        print(f"     created : {m['title']}")

    db.flush()
    return key_to_id


def seed_participants(db, mid: dict, uid: dict) -> None:
    print("  -> Participants")
    rows = [
        ("mtg-001", "ashishlokapure19@gmail.com", "Ashish Lokapure",  "ashishlokapure19@gmail.com", "organizer"),
        ("mtg-001", "priya.sharma@demo.com",       "Priya Sharma",     "priya.sharma@demo.com",      "attendee"),
        ("mtg-001", "rahul.mehta@demo.com",        "Rahul Mehta",      "rahul.mehta@demo.com",       "attendee"),
        ("mtg-001", "sneha.patil@demo.com",        "Sneha Patil",      "sneha.patil@demo.com",       "attendee"),
        ("mtg-002", "priya.sharma@demo.com",       "Priya Sharma",     "priya.sharma@demo.com",      "organizer"),
        ("mtg-002", "rahul.mehta@demo.com",        "Rahul Mehta",      "rahul.mehta@demo.com",       "attendee"),
        ("mtg-002", "arjun.nair@demo.com",         "Arjun Nair",       "arjun.nair@demo.com",        "attendee"),
        ("mtg-003", "ashishlokapure19@gmail.com",  "Ashish Lokapure",  "ashishlokapure19@gmail.com", "organizer"),
        ("mtg-003", "rahul.mehta@demo.com",        "Rahul Mehta",      "rahul.mehta@demo.com",       "attendee"),
        ("mtg-003", "sneha.patil@demo.com",        "Sneha Patil",      "sneha.patil@demo.com",       "attendee"),
        ("mtg-003", "arjun.nair@demo.com",         "Arjun Nair",       "arjun.nair@demo.com",        "attendee"),
    ]
    count = 0
    for mkey, uemail, pname, pemail, prole in rows:
        exists = db.execute(
            text("SELECT 1 FROM meeting_participants WHERE meeting_id=:m AND user_id=:u"),
            {"m": mid[mkey], "u": uid[uemail]}
        ).first()
        if exists:
            continue
        db.execute(text("""
            INSERT INTO meeting_participants
                (id, meeting_id, user_id, participant_name, participant_email, participant_role)
            VALUES (:id, :m, :u, :pn, :pe, :pr)
        """), {
            "id": str(uuid4()), "m": mid[mkey], "u": uid[uemail],
            "pn": pname, "pe": pemail, "pr": prole,
        })
        count += 1
    db.flush()
    print(f"     {count} participants inserted")


def seed_transcripts(db, mid: dict) -> None:
    print("  -> Transcripts")
    transcripts = [
        {
            "mkey": "mtg-001",
            "text": "Ashish: Let's start with the Q1 roadmap. Priya, what's the status on auth? Priya: We need to implement refresh token rotation. Rahul can own that. Rahul: Sure, I can have it done in 2 days. Ashish: Great. Sneha, can you handle the onboarding wireframes? Sneha: Yes, I'll deliver by end of next week.",
            "cleaned": "Ashish opened the Q1 roadmap discussion. Priya proposed implementing refresh token rotation, assigned to Rahul with a 2-day deadline. Sneha agreed to deliver onboarding wireframes by end of next week.",
            "words": 58, "lang": "en", "conf": 0.97,
        },
        {
            "mkey": "mtg-002",
            "text": "Priya: Sprint 12 kickoff. Arjun, you're on dashboard redesign. Arjun: Got it, I'll have it done in 20 hours. Priya: Sneha, connection pooling is done right? Sneha: Yes, completed yesterday.",
            "cleaned": "Priya kicked off Sprint 12. Arjun assigned to dashboard redesign with a 20-hour deadline. Sneha confirmed PostgreSQL connection pooling is complete.",
            "words": 38, "lang": "en", "conf": 0.95,
        },
    ]
    count = 0
    for t in transcripts:
        exists = db.execute(
            text("SELECT 1 FROM meeting_transcripts WHERE meeting_id=:m"),
            {"m": mid[t["mkey"]]}
        ).first()
        if exists:
            continue
        db.execute(text("""
            INSERT INTO meeting_transcripts
                (id, meeting_id, transcript_text, cleaned_text, word_count,
                 language, confidence_score, transcript_format)
            VALUES (:id, :m, :txt, :clean, :wc, :lang, :conf, 'text/plain')
        """), {
            "id": str(uuid4()), "m": mid[t["mkey"]],
            "txt": t["text"], "clean": t["cleaned"],
            "wc": t["words"], "lang": t["lang"], "conf": t["conf"],
        })
        count += 1
    db.flush()
    print(f"     {count} transcripts inserted")


def seed_summaries(db, mid: dict) -> None:
    print("  -> Summaries")
    import json
    summaries = [
        {
            "mkey": "mtg-001",
            "summary": "The team reviewed Q1 product goals. Key decisions were made around authentication improvements, UI redesign, and test coverage. Six action items were assigned with clear owners and deadlines.",
            "decisions": json.dumps(["Adopt JWT refresh token rotation.", "Redesign dashboard KPI cards.", "Achieve 80% test coverage on email service."]),
            "action_items": json.dumps(["Rahul: Implement JWT refresh token rotation", "Sneha: Deliver onboarding wireframes", "Rahul: Write unit tests for email service (overdue)"]),
            "risks": json.dumps(["Token rotation may break existing mobile clients.", "Wireframe delivery depends on design system availability."]),
            "model": "gpt-4.1",
        },
        {
            "mkey": "mtg-002",
            "summary": "Sprint 12 kickoff completed. Stories were estimated and assigned. Dashboard redesign and connection pooling are the top priorities this sprint.",
            "decisions": json.dumps(["Arjun owns dashboard KPI card redesign.", "Sneha to complete PostgreSQL connection pooling setup."]),
            "action_items": json.dumps(["Arjun: Redesign dashboard KPI cards (due in 20 hours)", "Sneha: Set up PostgreSQL connection pooling (completed)"]),
            "risks": json.dumps(["Tight deadline on dashboard redesign."]),
            "model": "gpt-4.1",
        },
    ]
    count = 0
    for s in summaries:
        exists = db.execute(
            text("SELECT 1 FROM meeting_summaries WHERE meeting_id=:m"),
            {"m": mid[s["mkey"]]}
        ).first()
        if exists:
            continue
        db.execute(text("""
            INSERT INTO meeting_summaries
                (id, meeting_id, executive_summary, decisions, action_items, risks, model_name)
            VALUES (:id, :m, :summary,
                CAST(:decisions AS jsonb),
                CAST(:action_items AS jsonb),
                CAST(:risks AS jsonb),
                :model)
        """), {
            "id": str(uuid4()), "m": mid[s["mkey"]],
            "summary": s["summary"], "decisions": s["decisions"],
            "action_items": s["action_items"], "risks": s["risks"],
            "model": s["model"],
        })
        count += 1
    db.flush()
    print(f"     {count} summaries inserted")


def seed_tasks(db, mid: dict, uid: dict) -> None:
    print("  -> Tasks")
    tasks = [
        {
            "key": "task-001",
            "mkey": "mtg-001",
            "assignee": "rahul.mehta@demo.com",
            "assigner": "priya.sharma@demo.com",
            "title": "Implement JWT refresh token rotation",
            "desc": "Update the auth service to rotate refresh tokens on every use.",
            "priority": TaskPriority.high.value,
            "status": TaskStatus.pending.value,
            "due": utcnow() + timedelta(days=2),
            "reminder": True,
        },
        {
            "key": "task-002",
            "mkey": "mtg-001",
            "assignee": "sneha.patil@demo.com",
            "assigner": "priya.sharma@demo.com",
            "title": "Design onboarding flow wireframes",
            "desc": "Create Figma wireframes for the new user onboarding flow.",
            "priority": TaskPriority.medium.value,
            "status": TaskStatus.in_progress.value,
            "due": utcnow() + timedelta(days=5),
            "reminder": True,
        },
        {
            "key": "task-003",
            "mkey": "mtg-002",
            "assignee": "arjun.nair@demo.com",
            "assigner": "priya.sharma@demo.com",
            "title": "Redesign dashboard KPI cards",
            "desc": "Update the dashboard UI to show real-time KPI metrics.",
            "priority": TaskPriority.medium.value,
            "status": TaskStatus.pending.value,
            "due": utcnow() + timedelta(hours=20),
            "reminder": True,
        },
        {
            "key": "task-004",
            "mkey": "mtg-001",
            "assignee": "rahul.mehta@demo.com",
            "assigner": "priya.sharma@demo.com",
            "title": "Write unit tests for email service",
            "desc": "Cover all EmailService methods with pytest unit tests.",
            "priority": TaskPriority.high.value,
            "status": TaskStatus.overdue.value,
            "due": utcnow() - timedelta(days=3),
            "reminder": True,
        },
        {
            "key": "task-005",
            "mkey": "mtg-002",
            "assignee": "sneha.patil@demo.com",
            "assigner": "priya.sharma@demo.com",
            "title": "Set up PostgreSQL connection pooling",
            "desc": "Configure pgBouncer for production connection pooling.",
            "priority": TaskPriority.low.value,
            "status": TaskStatus.completed.value,
            "due": utcnow() - timedelta(days=1),
            "completion_date": utcnow() - timedelta(hours=5),
            "reminder": False,
        },
        {
            "key": "task-006",
            "mkey": "mtg-003",
            "assignee": "rahul.mehta@demo.com",
            "assigner": "ashishlokapure19@gmail.com",
            "title": "Deploy email notification system to staging",
            "desc": "Deploy and smoke-test the full email notification pipeline on staging.",
            "priority": TaskPriority.critical.value,
            "status": TaskStatus.in_progress.value,
            "due": utcnow() + timedelta(days=1),
            "reminder": True,
        },
    ]

    for t in tasks:
        exists = db.execute(
            text("SELECT 1 FROM tasks WHERE title=:title AND meeting_id=:m"),
            {"title": t["title"], "m": mid[t["mkey"]]}
        ).first()
        if exists:
            print(f"     skip    : {t['title']}")
            continue
        db.execute(text("""
            INSERT INTO tasks
                (id, meeting_id, assignee_id, assigned_by_id, title, description,
                 priority, status, due_date, completion_date,
                 reminder_enabled, reminder_interval_hours)
            VALUES
                (:id, :m, :assignee, :assigner, :title, :desc,
                 :priority, :status, :due, :comp,
                 :reminder, 24)
        """), {
            "id": str(uuid4()),
            "m": mid[t["mkey"]],
            "assignee": uid[t["assignee"]],
            "assigner": uid[t["assigner"]],
            "title": t["title"],
            "desc": t["desc"],
            "priority": t["priority"],
            "status": t["status"],
            "due": t["due"],
            "comp": t.get("completion_date"),
            "reminder": t["reminder"],
        })
        print(f"     created : [{t['status'].upper()}] {t['title']}")

    db.flush()


def seed_data() -> None:
    db = SessionLocal()
    try:
        print("Seeding demo data...")
        uid = seed_users(db)
        mid = seed_meetings(db, uid)
        seed_participants(db, mid, uid)
        seed_transcripts(db, mid)
        seed_summaries(db, mid)
        seed_tasks(db, mid, uid)
        db.commit()

        print()
        print("=" * 66)
        print("  DATABASE SEEDED SUCCESSFULLY")
        print("=" * 66)
        print()
        print(f"  {'Role':<12} {'Email':<42} Password")
        print(f"  {'-'*12} {'-'*42} {'-'*10}")
        for u in DEMO_USERS:
            print(f"  {u['role']:<12} {u['email']:<42} {DEMO_PASSWORD}")
        print()
        print("  Meetings : 3  |  Tasks : 6  |  Participants : 11  |  Summaries : 2")
        print()

    except Exception as e:
        db.rollback()
        print(f"\n  SEED FAILED: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migrations()
    create_tables()
    seed_data()
