# Quick Start Guide

## 1. Start the Server

### Option A: Use the CMD file (Easiest)
Navigate to the project folder in File Explorer, then:
- Double-click `start-server.cmd`
- This will open a terminal window showing the server running
- Keep this window open!

### Option B: In VS Code Terminal
Make sure you're in the correct directory:
```powershell
cd C:\Users\LOGAN\Desktop\protech
php -S 127.0.0.1:8001 router.php
```

### Option C: Use Command Prompt
```cmd
cd C:\Users\LOGAN\Desktop\protech
start-server.cmd
```

## 2. Access the Application

Open your browser and go to:
- **Home:** http://127.0.0.1:8001
- **Login:** http://127.0.0.1:8001/auth.html

## 3. Test Login

Use these credentials:
- Email: `john@example.com`
- Password: `password123`

## 4. Debug Login Issues

If login doesn't redirect, test it with:
http://127.0.0.1:8001/test_login_simple.php

This will show you what's happening with the login.

## Troubleshooting

**"Page not found" or "Can't connect"**
- Make sure the server is running (check the terminal window)
- Make sure you're using the correct URL: http://127.0.0.1:8001

**Login doesn't redirect**
- Check browser console (F12) for JavaScript errors
- Check the server terminal for PHP errors
- Test with: http://127.0.0.1:8001/test_login_simple.php

**Database connection errors**
- Make sure PostgreSQL is running
- Check that password in config.php matches your PostgreSQL password
- Make sure protech_db database exists
