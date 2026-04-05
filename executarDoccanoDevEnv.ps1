param(
    [string]$AdminUser = "admin",
    [string]$AdminEmail = "admin@example.com",
    [string]$AdminPassword = "admin"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "[1/3] Initializing backend database and admin user..." -ForegroundColor Cyan
Set-Location (Join-Path $root "backend")
poetry run python manage.py migrate
poetry run python manage.py create_roles
poetry run python manage.py create_admin --noinput --username $AdminUser --email $AdminEmail --password $AdminPassword

Write-Host "[2/3] Starting backend (Django) on http://localhost:8000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$($root.Replace("'","''"))\\backend'; poetry run python manage.py runserver"
)

Write-Host "[3/3] Starting Celery worker and frontend..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$($root.Replace("'","''"))\\backend'; `$env:REDIS_URL='redis://localhost:6379/0'; poetry run celery --app=config worker --loglevel=INFO --concurrency=1 --pool=solo"
)

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "Set-Location '$($root.Replace("'","''"))\\frontend'; corepack yarn dev"
)

Write-Host "Done. Frontend: http://localhost:3000 | Backend: http://localhost:8000" -ForegroundColor Green
Write-Host "Tip: If Celery complains about broker, run Docker Redis/RabbitMQ/Postgres first." -ForegroundColor Yellow
