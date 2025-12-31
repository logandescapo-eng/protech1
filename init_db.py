"""
Quick script to initialize Railway database
Run this locally with Railway connection string
"""

import sys
import psycopg2
from urllib.parse import urlparse

# You can pass DATABASE_URL as command line argument or set it here
if len(sys.argv) > 1:
    DATABASE_URL = sys.argv[1]
else:
    # Paste your Railway connection string here temporarily
    DATABASE_URL = input("Paste your Railway DATABASE_URL: ").strip()

if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("Connecting...")
try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    print("Reading database.sql...")
    with open('database.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print("Executing SQL...")
    # Execute the entire SQL file
    cur.execute(sql)
    conn.commit()
    
    print("✅ Database initialized successfully!")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
