#!/bin/bash

# Cleanup script to reset development environment for Doccano Extended.
# Use this if you encounter migration issues or want to start over.

set -e

echo "Cleaning up Doccano Development Environment..."
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND="$SCRIPT_DIR/backend"
FRONTEND="$SCRIPT_DIR/frontend"

# Cleanup backend database files
echo "[INFO] Removing database files..."
rm -f "$BACKEND"/*.sqlite3*
rm -f "$BACKEND"/celery-results.sqlite3*

# Cleanup upload directories
echo "[INFO] Removing upload directories..."
rm -rf "$BACKEND/filepond-temp-uploads"
rm -rf "$BACKEND/media"

# Cleanup logs
echo "[INFO] Removing log files..."
find "$BACKEND" -name "*.log" -delete 2>/dev/null || true

# Cleanup pycache
echo "[INFO] Removing Python cache..."
find "$BACKEND" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Cleanup frontend
echo "[INFO] Removing frontend build artifacts..."
rm -rf "$FRONTEND/.nuxt"
rm -rf "$FRONTEND/dist"

echo ""
echo "[SUCCESS] Cleanup complete!"
echo ""
echo "Next steps:"
echo "  1. ./executarDoccanoDevEnv.sh   (to start fresh)"
echo ""
