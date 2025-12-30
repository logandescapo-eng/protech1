# PowerShell script to start PHP server in VS Code terminal
# This ensures the server runs in the current terminal window

Write-Host "Starting PHP Development Server..." -ForegroundColor Cyan
Write-Host ""

# Find PHP executable
$phpPath = (Get-Command php -ErrorAction SilentlyContinue).Source
if (-not $phpPath) {
    Write-Host "Error: PHP not found in PATH" -ForegroundColor Red
    exit 1
}

Write-Host "Using PHP: $phpPath" -ForegroundColor Gray
Write-Host ""
Write-Host "Server will be available at: http://127.0.0.1:8001" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Start PHP server using full path (this should run in current terminal)
& $phpPath -S 127.0.0.1:8001 router.php
