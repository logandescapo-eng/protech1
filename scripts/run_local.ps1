# Start ProTech locally with manage.py runserver (Windows PowerShell)
Set-Location $PSScriptRoot\..

if (-not (Test-Path .env)) {
    Copy-Item .env.dev.example .env
    Write-Host "Created .env from .env.dev.example"
}

Write-Host "Starting PostgreSQL and Redis..."
docker compose up -d db redis
Start-Sleep -Seconds 6

Write-Host "Applying migrations..."
python manage.py migrate

Write-Host "Seeding demo data (if empty)..."
python manage.py seed_demo --if-empty

Write-Host ""
Write-Host "Open http://127.0.0.1:8000"
Write-Host "Login: john@example.com / password123"
Write-Host ""
python manage.py runserver
