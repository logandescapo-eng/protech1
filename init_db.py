"""
Initialize ProTech database from database.sql
Usage: python init_db.py <DATABASE_URL>
"""

import sys
import psycopg2
import bcrypt

DEMO_PASSWORD = "password123"
DEMO_EMAILS = [
    "john@example.com",
    "mike@example.com",
    "sarah@example.com",
    "david@example.com",
]


def normalize_url(url):
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def split_sql(content):
    """Split SQL file into statements (handles $$ ... $$ blocks)."""
    statements = []
    buf = []
    in_dollar = False

    for line in content.split("\n"):
        if not in_dollar:
            stripped = line.strip()
            if stripped.startswith("--") or not stripped:
                continue

        buf.append(line)

        if "$$" in line and line.count("$$") % 2 == 1:
            in_dollar = not in_dollar

        if line.rstrip().endswith(";") and not in_dollar:
            stmt = "\n".join(buf).strip()
            if stmt:
                statements.append(stmt)
            buf = []

    return statements


def fix_demo_passwords(cur):
    """Ensure demo accounts use password123 (works even if seed hash was wrong)."""
    new_hash = bcrypt.hashpw(
        DEMO_PASSWORD.encode("utf-8"), bcrypt.gensalt(rounds=10)
    ).decode("utf-8")

    print("\nSetting demo account passwords to 'password123'...")
    for email in DEMO_EMAILS:
        cur.execute(
            "UPDATE users SET password = %s WHERE email = %s RETURNING name",
            (new_hash, email),
        )
        row = cur.fetchone()
        if row:
            print(f"  Updated {row[0]} ({email})")
        else:
            print(f"  Skipped {email} (not in database)")


def main():
    if len(sys.argv) > 1:
        database_url = sys.argv[1].strip()
    else:
        database_url = input("Paste your DATABASE_URL: ").strip()

    database_url = normalize_url(database_url)

    print("Connecting...")
    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    print("Reading database.sql...")
    with open("database.sql", "r", encoding="utf-8") as f:
        statements = split_sql(f.read())

    print(f"Running {len(statements)} SQL statements...")
    for i, stmt in enumerate(statements, 1):
        try:
            cur.execute(stmt)
        except Exception as e:
            conn.rollback()
            print(f"\nFailed on statement {i}/{len(statements)}: {e}")
            print(stmt[:300] + ("..." if len(stmt) > 300 else ""))
            sys.exit(1)

    conn.commit()
    print("Schema and seed data applied.")

    fix_demo_passwords(cur)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    print(f"\nDone. Users in database: {count}")
    print("\nLogin with:")
    print("  Email:    john@example.com")
    print("  Password: password123")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
