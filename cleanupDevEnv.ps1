#Requires -Version 5.1

<#
.SYNOPSIS
Cleanup script to reset development environment for Doccano Extended.

.DESCRIPTION
This script removes generated files and databases to allow a fresh start.
Use this if you encounter migration issues or want to start over.

.EXAMPLE
.\cleanupDevEnv.ps1
#>

Write-Host "Cleaning up Doccano Development Environment..." -ForegroundColor Yellow
Write-Host ""

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"

# Cleanup backend database files
Write-Host "[INFO] Removing database files..."
Get-ChildItem -Path "$backend" -Filter "*.sqlite3*" -ErrorAction SilentlyContinue | Remove-Item -Force
Get-ChildItem -Path "$backend" -Filter "celery-results.sqlite3*" -ErrorAction SilentlyContinue | Remove-Item -Force

# Cleanup upload directories
Write-Host "[INFO] Removing upload directories..."
Remove-Item "$backend\filepond-temp-uploads" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$backend\media" -Recurse -Force -ErrorAction SilentlyContinue

# Cleanup logs
Write-Host "[INFO] Removing log files..."
Get-ChildItem -Path "$backend" -Filter "*.log" -ErrorAction SilentlyContinue | Remove-Item -Force

# Cleanup pycache
Write-Host "[INFO] Removing Python cache..."
Get-ChildItem -Path "$backend" -Directory -Filter "__pycache__" -Recurse -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

# Cleanup frontend
Write-Host "[INFO] Removing frontend build artifacts..."
Remove-Item "$frontend\.nuxt" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$frontend\dist" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "[SUCCESS] Cleanup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. .\executarDoccanoDevEnv.ps1   (to start fresh)"
Write-Host ""
