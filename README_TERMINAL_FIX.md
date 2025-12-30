# Fix for VS Code Terminal Issue

If running `php -S localhost:8001 router.php` opens an external XAMPP terminal instead of running in VS Code terminal, here are solutions:

## Solution 1: Use PowerShell Script (Recommended)

Run this in VS Code terminal:
```powershell
.\start-server-vscode.ps1
```

This will run the server in the current VS Code terminal window.

## Solution 2: Use Full Path to PHP

Find your PHP path and use it directly:
```powershell
# Find PHP path
Get-Command php | Select-Object Source

# Then use full path (example):
& "C:\xampp\htdocs\protech\php\php.exe" -S 127.0.0.1:8001 router.php
```

## Solution 3: Use Batch File (Opens New Window)

Double-click `start-server.bat` - this will open a new terminal window but will work.

## Solution 4: Run Directly in PowerShell

Make sure you're in PowerShell (not CMD) in VS Code terminal and run:
```powershell
cd C:\Users\LOGAN\Desktop\protech
php -S 127.0.0.1:8001 router.php
```

If it still opens external terminal, the PHP executable might be a batch file wrapper. Check with:
```powershell
Get-Content (Get-Command php).Source | Select-Object -First 10
```
