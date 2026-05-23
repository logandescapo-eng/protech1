"""Apply escrow tables to an existing database."""
import sys
import psycopg2
from init_db import split_sql, normalize_url

if len(sys.argv) < 2:
    print("Usage: python migrate_escrow.py <DATABASE_URL>")
    sys.exit(1)

url = normalize_url(sys.argv[1].strip())

with open('migrations/escrow.sql', 'r', encoding='utf-8') as f:
    statements = split_sql(f.read())

conn = psycopg2.connect(url)
cur = conn.cursor()
print(f"Running {len(statements)} escrow statements...")
for i, stmt in enumerate(statements, 1):
    try:
        cur.execute(stmt)
    except Exception as e:
        err = str(e).lower()
        if 'already exists' in err or 'duplicate' in err:
            continue
        print(f"Statement {i} failed: {e}")
        conn.rollback()
        sys.exit(1)
conn.commit()
cur.close()
conn.close()
print("Escrow migration applied successfully.")
