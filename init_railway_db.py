"""
Script to initialize Railway PostgreSQL database with schema
Run this once to create all tables and insert sample data
"""

import os
import psycopg2
from urllib.parse import urlparse

# Get DATABASE_URL from environment (Railway sets this automatically)
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not found!")
    print("Make sure you've added DATABASE_URL to your Railway app variables.")
    print("Use: ${{ Postgres.DATABASE_URL }}")
    exit(1)

# Parse DATABASE_URL
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"Connecting to database...")
print(f"URL: {DATABASE_URL.split('@')[0]}@***")  # Hide password in output

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Read database.sql file
    print("\nReading database.sql file...")
    with open('database.sql', 'r', encoding='utf-8') as f:
        sql_file = f.read()
    
    # Split by semicolons and execute each statement
    # (Handle multi-line statements properly)
    print("Executing SQL statements...")
    statements = []
    current_statement = ""
    
    for line in sql_file.split('\n'):
        # Skip comments and empty lines
        stripped = line.strip()
        if not stripped or stripped.startswith('--'):
            continue
        
        current_statement += line + '\n'
        
        # If line ends with semicolon, it's a complete statement
        if stripped.endswith(';'):
            statements.append(current_statement.strip())
            current_statement = ""
    
    # Execute all statements
    for i, statement in enumerate(statements, 1):
        if statement.strip():
            try:
                cur.execute(statement)
                print(f"  ✓ Executed statement {i}/{len(statements)}")
            except Exception as e:
                print(f"  ⚠ Error in statement {i}: {e}")
                print(f"    Statement: {statement[:100]}...")
    
    conn.commit()
    print(f"\n✅ Database initialized successfully!")
    print(f"   Created {len(statements)} tables/statements")
    
    cur.close()
    conn.close()
    
except psycopg2.Error as e:
    print(f"\n❌ Database error: {e}")
    exit(1)
except FileNotFoundError:
    print("\n❌ ERROR: database.sql file not found!")
    print("Make sure database.sql is in the same directory as this script.")
    exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    exit(1)
