#Requires -Version 5.1

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$dockerDir = Join-Path $root "docker"
$composeFile = "docker-compose.prod.yml"
$envFile = Join-Path $root ".env"

Set-Location -Path $dockerDir

$useComposeV1 = $false
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    $useComposeV1 = $true
}

if ($useComposeV1) {
    if (Test-Path $envFile) {
        docker-compose -f $composeFile --env-file $envFile up -d --build
    } else {
        docker-compose -f $composeFile up -d --build
    }
} elseif (Get-Command docker -ErrorAction SilentlyContinue) {
    if (Test-Path $envFile) {
        docker compose -f $composeFile --env-file $envFile up -d --build
    } else {
        docker compose -f $composeFile up -d --build
    }
} else {
    Write-Host "Docker is not installed or not on PATH." -ForegroundColor Red
    exit 1
}