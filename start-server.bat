@echo off
echo Starting PHP Development Server...
echo.
echo Server will be available at: http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop the server
echo.
cd /d "%~dp0"
php -S 127.0.0.1:8000 router.php

