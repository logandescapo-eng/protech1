"""
Check if users exist in database and test password
"""

import sys
import psycopg2
import bcrypt

if len(sys.argv) < 2:
    print("Usage: python check_users.py <DATABASE_URL>")
    sys.exit(1)

DATABASE_URL = sys.argv[1]

if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print("Connecting to database...")
try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Check if users table exists and has data
    print("\nChecking users table...")
    cur.execute("SELECT COUNT(*) FROM users;")
    count = cur.fetchone()[0]
    print(f"Total users in database: {count}")
    
    if count == 0:
        print("\n❌ NO USERS FOUND!")
        print("The database.sql INSERT statements might not have run.")
        print("You may need to re-run the init script.")
    else:
        print("\n✅ Users found! Checking john@example.com...")
        cur.execute("SELECT id, name, email, password, user_type FROM users WHERE email = 'john@example.com';")
        user = cur.fetchone()
        
        if user:
            user_id, name, email, password_hash, user_type = user
            print(f"   ID: {user_id}")
            print(f"   Name: {name}")
            print(f"   Email: {email}")
            print(f"   Type: {user_type}")
            print(f"   Password hash: {password_hash[:20]}...")
            
            # Test password
            print("\nTesting password 'password123'...")
            test_password = "password123"
            
            # Convert $2y$ to $2b$ if needed
            stored_hash = password_hash
            if stored_hash.startswith('$2y$'):
                stored_hash = '$2b$' + stored_hash[4:]
                print(f"   Converted hash: $2y$ -> $2b$")
            
            try:
                if bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8')):
                    print("   ✅ Password 'password123' is CORRECT!")
                else:
                    print("   ❌ Password 'password123' is INCORRECT!")
                    print("   The hash in database might be for a different password.")
                    
                    # Try to see what the hash represents
                    print("\n   Trying to generate new hash for 'password123'...")
                    new_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    print(f"   New hash would be: {new_hash[:30]}...")
                    
            except Exception as e:
                print(f"   ❌ Error checking password: {e}")
        else:
            print("   ❌ john@example.com not found in database!")
    
    # List all users
    print("\nAll users in database:")
    cur.execute("SELECT id, name, email, user_type FROM users ORDER BY id;")
    users = cur.fetchall()
    for u in users:
        print(f"   {u[0]}: {u[1]} ({u[2]}) - {u[3]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
