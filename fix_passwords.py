"""
Fix user passwords - generate new bcrypt hashes for password123
"""

import sys
import psycopg2
import bcrypt

if len(sys.argv) < 2:
    print("Usage: python fix_passwords.py <DATABASE_URL>")
    sys.exit(1)

DATABASE_URL = sys.argv[1]

if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("Connecting to database...")
try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Generate new hash for password123
    new_password = "password123"
    new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print(f"\nGenerated new hash for 'password123':")
    print(f"   {new_hash[:50]}...")
    
    test_users = [
        ("John Client", "john@example.com", "+1234567890", "user"),
        ("Mike Plumber", "mike@example.com", "+1234567891", "worker"),
        ("Sarah Electrician", "sarah@example.com", "+1234567892", "worker"),
        ("David Cleaner", "david@example.com", "+1234567893", "worker"),
    ]

    print("\nUpdating or creating demo users...")
    for name, email, phone, user_type in test_users:
        cur.execute(
            """
            INSERT INTO users (name, email, phone, password, user_type)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (email) DO UPDATE SET password = EXCLUDED.password
            RETURNING name
            """,
            (name, email, phone, new_hash, user_type),
        )
        print(f"   OK {cur.fetchone()[0]} ({email})")
    
    conn.commit()
    print("\n✅ All passwords updated successfully!")
    print("\nYou can now login with:")
    print("   Email: john@example.com (or any test email)")
    print("   Password: password123")
    
    # Verify one password works
    print("\nVerifying password works...")
    cur.execute("SELECT password FROM users WHERE email = 'john@example.com';")
    stored_hash = cur.fetchone()[0]
    if bcrypt.checkpw(new_password.encode('utf-8'), stored_hash.encode('utf-8')):
        print("   ✅ Password verification successful!")
    else:
        print("   ❌ Password verification failed (this shouldn't happen)")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
