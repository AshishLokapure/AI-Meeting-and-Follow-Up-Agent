import psycopg2

DSN = "postgresql://postgres:Ashish19@localhost:5432/AI_Meeting_Flow"

DDL = [
    "ALTER TABLE employees ALTER COLUMN name DROP NOT NULL",
    "ALTER TABLE employees ALTER COLUMN is_active DROP NOT NULL",
    "ALTER TABLE employees ALTER COLUMN is_active SET DEFAULT true",
]

conn = psycopg2.connect(DSN)
conn.autocommit = True
cur = conn.cursor()
for sql in DDL:
    print("->", sql)
    cur.execute(sql)

cur.execute("SELECT column_name, is_nullable FROM information_schema.columns WHERE table_name='employees' AND column_name IN ('name','is_active') ORDER BY column_name")
for row in cur.fetchall():
    print("  col:", row)

cur.close()
conn.close()
print("DONE")
