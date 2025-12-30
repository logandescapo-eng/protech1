# How to Reset PostgreSQL Password

Since the password `postgres123` is not working, you need to either:
1. Find your actual password (if you can connect via pgAdmin)
2. Reset the password to match what's in config.php

## Option 1: Check Password in pgAdmin (Easiest)

If you can connect via pgAdmin:
1. Open pgAdmin
2. Right-click on your PostgreSQL server
3. Go to Properties → Connection tab
4. Check what password is saved there (you might need to look at the saved password or reconnect)

## Option 2: Reset Password via pgAdmin

1. Open pgAdmin
2. Connect to your PostgreSQL server (if you can)
3. Navigate to: Login/Group Roles → postgres → right-click → Properties
4. Go to the "Definition" tab
5. Enter new password: `postgres123`
6. Click Save

## Option 3: Reset Password via Windows Authentication (If pgAdmin doesn't work)

If you can't connect at all, you can reset using Windows authentication:

1. Open Command Prompt as Administrator
2. Find your PostgreSQL bin directory (usually `C:\Program Files\PostgreSQL\17\bin`)
3. Run this command:
   ```
   psql -U postgres -d postgres
   ```
   (This should connect without a password if you're using Windows authentication)

4. Once connected, run:
   ```sql
   ALTER USER postgres WITH PASSWORD 'postgres123';
   ```

5. Type `\q` to exit

## Option 4: Update config.php with Correct Password

Once you know your actual password, update `config.php` line 20:
```php
define('DB_PASS', 'your_actual_password');
```
