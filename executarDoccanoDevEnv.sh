#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$ROOT_DIR/backend"
FRONTEND="$ROOT_DIR/frontend"
ENV_FILE="$BACKEND/.env"

# ======================================
# Generate .env if it doesn't exist or is incomplete
# ======================================
GENERATE_ENV=false
if [ ! -f "$ENV_FILE" ]; then
    GENERATE_ENV=true
    echo "[INFO] .env file not found, generating..."
else
    # Check if .env has DEBUG=True (sign of development environment)
    if ! grep -q "DEBUG.*True" "$ENV_FILE"; then
        GENERATE_ENV=true
        echo "[INFO] .env exists but DEBUG!=True, regenerating for development..."
    fi
fi

if [ "$GENERATE_ENV" = true ]; then
    # Generate SECRET_KEY
    SECRET_KEY=$(cd "$BACKEND" && poetry run python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    
    # Create .env with development settings
    cat > "$ENV_FILE" << EOF
# ================================
# Doccano Development Environment
# ================================
# Generated automatically by executarDoccanoDevEnv.sh
# DO NOT commit .env to version control!

# ================================
# Django Settings
# ================================
SECRET_KEY=$SECRET_KEY
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,192.168.56.1,192.168.1.1

# ================================
# Database Configuration
# ================================
DATABASE_URL=sqlite:///db.sqlite3
DATABASE_CONN_MAX_AGE=500

# ================================
# CORS & Security Settings
# ================================
# Frontend can be accessed from multiple addresses.
# Add your specific IP here if frontend is on a different machine/network.
# Common WSL IPs: 192.168.56.1, 192.168.1.*, 172.x.x.x
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://192.168.56.1:3000,http://192.168.1.1:3000,https://localhost:3000,https://127.0.0.1:3000,https://192.168.56.1:3000,https://192.168.1.1:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://192.168.56.1:3000,http://192.168.1.1:3000,https://localhost:3000,https://127.0.0.1:3000,https://192.168.56.1:3000,https://192.168.1.1:3000

# ================================
# Admin Credentials (CHANGE IN PRODUCTION!)
# ================================
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin
ADMIN_EMAIL=admin@example.com

# ================================
# Celery Configuration
# ================================
CELERY_BROKER_URL=sqla+sqlite:///db.sqlite3
CELERY_RESULT_BACKEND=db+sqlite:///celery-results.sqlite3

# ================================
# Logging
# ================================
LOG_LEVEL=INFO

# ================================
# Storage
# ================================
# For production, use cloud storage (AWS S3, etc.)
STORAGE_BACKEND=storages.backends.s3boto3.S3Boto3Storage
EOF
    
    echo "[OK] .env file created with development settings"
else
    echo "[OK] .env file is already configured for development"
fi

echo ""
echo "Starting Doccano Development Environment..."
echo "   Backend:  http://127.0.0.1:8000"
echo "   Frontend: http://192.168.56.1:3000 (or localhost:3000)"
echo "   Admin:    admin / admin"
echo ""

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "Stopping all services..."
    kill $PID_BACKEND $PID_CELERY $PID_FRONTEND 2>/dev/null || true
    wait $PID_BACKEND $PID_CELERY $PID_FRONTEND 2>/dev/null || true
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

if [[ "$(uname -s)" == "Darwin" ]]; then
    # macOS: Use Terminal.app for better UX
    echo "Starting services in separate Terminal windows..."
    
    # Migrate & create admin
    osascript -e "tell application \"Terminal\" to do script \"cd ${BACKEND} && poetry run python manage.py migrate && poetry run python manage.py create_roles && poetry run python manage.py create_admin --noinput --username admin --email admin@example.com --password admin 2>/dev/null || true && poetry run python manage.py runserver\""
    
    # Celery worker
    osascript -e "tell application \"Terminal\" to do script \"cd ${BACKEND} && poetry run celery --app=config worker --loglevel=INFO --concurrency=1\""
    
    # Frontend
    osascript -e "tell application \"Terminal\" to do script \"cd ${FRONTEND} && npm run dev\""
    
    echo "[OK] All services started in separate Terminal windows"
    echo "Press Ctrl+C in each window to stop the services"
else
    # Linux/WSL: Run in background with foreground output
    echo "Starting backend (Django)..."
    (
        cd "$BACKEND"
        poetry run python manage.py migrate
        poetry run python manage.py create_roles
        poetry run python manage.py create_admin --noinput --username admin --email admin@example.com --password admin 2>/dev/null || true
        poetry run python manage.py runserver
    ) &
    PID_BACKEND=$!
    
    # Wait a bit for backend to start
    sleep 3
    
    echo "Starting Celery worker..."
    (
        cd "$BACKEND"
        poetry run celery --app=config worker --loglevel=INFO --concurrency=1
    ) &
    PID_CELERY=$!
    
    # Wait a bit for celery to start
    sleep 2
    
    echo "Starting frontend (Nuxt)..."
    (
        cd "$FRONTEND"
        npm run dev
    ) &
    PID_FRONTEND=$!
    
    echo "[OK] All services started!"
    echo "Press Ctrl+C to stop all services"
    
    # Wait for all processes
    wait
fi
