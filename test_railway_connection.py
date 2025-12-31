"""
Quick test to see if we can connect to Railway database
"""

import sys
import psycopg2

if len(sys.argv) < 2:
    print("Usage: python test_railway_connection.py <DATABASE_URL>")
    print("\nGet DATABASE_URL from Railway:")
    print("1. Go to PostgreSQL service")
    print("2. Click 'Connect' button")
    print("3. Go to 'Public Network' tab")
    print("4. Click 'Show' next to Connection URL")
    print("5. Copy the entire URL (postgresql://...)")
    sys.exit(1)

DATABASE_URL = sys.argv[1]

# Fix postgres:// to postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"\nTesting connection...")
print(f"URL format: {DATABASE_URL.split('@')[0]}@***\n")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Test query
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"✅ SUCCESS! Connected to database!")
    print(f"   PostgreSQL version: {version[0][:50]}...")
    
    # Check if tables exist
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cur.fetchall()
    
    if tables:
        print(f"\n📊 Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
    else:
        print("\n⚠️  No tables found. Database is empty.")
        print("   You need to run database.sql to create tables.")
    
    cur.close()
    conn.close()
    
except psycopg2.OperationalError as e:
    print(f"❌ CONNECTION FAILED!")
    print(f"   Error: {e}")
    print(f"\n💡 Common issues:")
    print(f"   1. Make sure you're using PUBLIC NETWORK connection string")
    print(f"   2. Check if the URL is correct (copy entire string)")
    print(f"   3. Make sure password is visible (click 'Show' in Railway)")
    sys.exit(1)
except Exception as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)
