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
    
    # Update all test users
    test_emails = [
        'john@example.com',
        'mike@example.com',
        'sarah@example.com',
        'david@example.com'
    ]
    
    print("\nUpdating passwords for test users...")
    for email in test_emails:
        cur.execute(
            "UPDATE users SET password = %s WHERE email = %s RETURNING name;",
            (new_hash, email)
        )
        result = cur.fetchone()
        if result:
            print(f"   ✅ Updated {result[0]} ({email})")
        else:
            print(f"   ⚠️  {email} not found (skipping)")
    
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
