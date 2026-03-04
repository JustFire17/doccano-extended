#Requires -Version 5.1

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$envFile = Join-Path $backend ".env"

function Test-CommandExists {
    param([string]$CommandName)
    return [bool](Get-Command $CommandName -ErrorAction SilentlyContinue)
}

if (-not (Test-CommandExists "python")) {
    Write-Host "[ERROR] Python is not installed or not on PATH." -ForegroundColor Red
    exit 1
}

if (-not (Test-CommandExists "poetry")) {
    Write-Host "[ERROR] Poetry is not installed or not on PATH." -ForegroundColor Red
    exit 1
}

if (-not (Test-CommandExists "node")) {
    Write-Host "[ERROR] Node.js is not installed or not on PATH." -ForegroundColor Red
    exit 1
}

if (-not (Test-CommandExists "npm")) {
    Write-Host "[ERROR] npm is not installed or not on PATH." -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Ensuring backend dependencies are installed (poetry install)..."
Push-Location $backend
& poetry install
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    Write-Host "[ERROR] Failed to install backend dependencies." -ForegroundColor Red
    exit 1
}
Pop-Location

Write-Host "[INFO] Ensuring frontend dependencies are installed (npm install)..."
Push-Location $frontend
if (-not (Test-Path (Join-Path $frontend "node_modules"))) {
    & npm install
    if ($LASTEXITCODE -ne 0) {
        Pop-Location
        Write-Host "[ERROR] Failed to install frontend dependencies." -ForegroundColor Red
        exit 1
    }
}
Pop-Location

$generateEnv = $false
if (-not (Test-Path $envFile)) {
    $generateEnv = $true
    Write-Host "[INFO] .env file not found, generating..."
} else {
    $envContent = Get-Content $envFile -Raw
    if (($envContent -notmatch "DEBUG\s*=\s*True") -or ($envContent -notmatch "(^|`r?`n)SECRET_KEY\s*=")) {
        $generateEnv = $true
        Write-Host "[INFO] .env exists but is incomplete for development, regenerating..."
    }
}

if ($generateEnv) {
    Push-Location $backend
    $secretKey = & poetry run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>&1
    if (-not $secretKey) {
        $secretKey = "django-insecure-$(Get-Random 100000)-$(Get-Random 100000)-$(Get-Random 100000)"
    }
    Pop-Location

    $envText = @"
# ================================
# Doccano Development Environment
# ================================
# Generated automatically by executarDoccanoDevEnv.ps1
# DO NOT commit .env to version control!

SECRET_KEY=$secretKey
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.56.1,192.168.1.1

DATABASE_URL=sqlite:///db.sqlite3
DATABASE_CONN_MAX_AGE=500

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://192.168.56.1:3000,http://192.168.1.1:3000,https://localhost:3000,https://127.0.0.1:3000,https://192.168.56.1:3000,https://192.168.1.1:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://192.168.56.1:3000,http://192.168.1.1:3000,https://localhost:3000,https://127.0.0.1:3000,https://192.168.56.1:3000,https://192.168.1.1:3000

ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin
ADMIN_EMAIL=admin@example.com

CELERY_BROKER_URL=sqla+sqlite:///db.sqlite3
CELERY_RESULT_BACKEND=db+sqlite:///celery-results.sqlite3

LOG_LEVEL=INFO
STORAGE_BACKEND=storages.backends.s3boto3.S3Boto3Storage
"@

    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($envFile, $envText, $utf8NoBom)
    Write-Host "[OK] .env file created with development settings"
} else {
    Write-Host "[OK] .env file is already configured for development"
}

Write-Host ""
Write-Host "Starting Doccano Development Environment..."
Write-Host "  Backend:  http://127.0.0.1:8000"
Write-Host "  Frontend: http://localhost:3000 (or local network URL shown by Nuxt)"
Write-Host "  Admin:    admin / admin"
Write-Host ""

$backendCmd = @"
`$env:DJANGO_SETTINGS_MODULE='config.settings.development'
Set-Location '$backend'
Write-Host "[INFO] Running migrations..." -ForegroundColor Cyan
poetry run python manage.py migrate
if (`$LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Migrations failed!" -ForegroundColor Red
}
Write-Host "[INFO] Creating roles..." -ForegroundColor Cyan
poetry run python manage.py create_roles
Write-Host "[INFO] Creating admin user..." -ForegroundColor Cyan
poetry run python manage.py create_admin --noinput --username admin --email admin@example.com --password admin
Write-Host "[INFO] Starting Django development server..." -ForegroundColor Green
poetry run python manage.py runserver
"@

$celeryCmd = @"
`$env:DJANGO_SETTINGS_MODULE='config.settings.development'
Set-Location '$backend'
Write-Host "[INFO] Starting Celery worker..." -ForegroundColor Green
poetry run celery --app=config worker --loglevel=INFO --concurrency=1 --pool=solo
"@

$frontendCmd = @"
Set-Location '$frontend'
Write-Host "[INFO] Starting Nuxt frontend..." -ForegroundColor Green
npm run dev
"@

Start-Process powershell -ArgumentList @("-NoExit", "-Command", $backendCmd)
Start-Sleep -Seconds 3
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $celeryCmd)
Start-Sleep -Seconds 3
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $frontendCmd)

Write-Host "[OK] All services started in separate PowerShell windows"
Write-Host ""
Write-Host "[TIPS] Setup Tips:"
Write-Host "  - If backends fail, migrations may not have run. Check backend terminal for errors."
Write-Host "  - If frontend shows 'port in use', edit .env and change FRONTEND_PORT=3001"
Write-Host "  - To validate, run: .\quickSanityCheck.ps1"
Write-Host ""
Write-Host "[NEXT] Open http://localhost:3000 in your browser"