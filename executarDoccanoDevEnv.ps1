#Requires -Version 5.1

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$envFile = Join-Path $backend ".env"

$generateEnv = $false
if (-not (Test-Path $envFile)) {
    $generateEnv = $true
    Write-Host "[INFO] .env file not found, generating..."
} else {
    $envContent = Get-Content $envFile -Raw
    if ($envContent -notmatch "DEBUG\s*=\s*True") {
        $generateEnv = $true
        Write-Host "[INFO] .env exists but DEBUG!=True, regenerating for development..."
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

    Set-Content -Path $envFile -Value $envText -Encoding UTF8
    Write-Host "[OK] .env file created with development settings"
} else {
    Write-Host "[OK] .env file is already configured for development"
}

Write-Host ""
Write-Host "Starting Doccano Development Environment..."
Write-Host "  Backend:  http://127.0.0.1:8000"
Write-Host "  Frontend: http://localhost:3000"
Write-Host "  Admin:    admin / admin"
Write-Host ""

$backendCmd = "cd '$backend'; poetry run python manage.py migrate; poetry run python manage.py create_roles; poetry run python manage.py create_admin --noinput --username admin --email admin@example.com --password admin 2>`$null; poetry run python manage.py runserver"
$celeryCmd = "cd '$backend'; poetry run celery --app=config worker --loglevel=INFO --concurrency=1"
$frontendCmd = "cd '$frontend'; npm run dev"

Start-Process powershell -ArgumentList @("-NoExit", "-Command", $backendCmd)
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $celeryCmd)
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList @("-NoExit", "-Command", $frontendCmd)

Write-Host "[OK] All services started in separate PowerShell windows"