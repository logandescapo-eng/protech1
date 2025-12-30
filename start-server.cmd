@echo off
cd /d "%~dp0"
echo Starting PHP Development Server...
echo.
echo Server will be available at: http://127.0.0.1:8001
echo.
echo Press Ctrl+C to stop the server
echo.
php -S 127.0.0.1:8001 router.php
