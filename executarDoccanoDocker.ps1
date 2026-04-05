param(
    [ValidateSet("up", "down", "logs", "ps")]
    [string]$Action = "up"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$composeArgs = @("-f", "docker/docker-compose.prod.yml", "--env-file", "docker/.env")

Set-Location $root

switch ($Action) {
    "up" {
        docker compose @composeArgs up -d --build
        docker compose @composeArgs ps
        Write-Host "App: http://localhost" -ForegroundColor Green
        Write-Host "Flower: http://localhost:5555" -ForegroundColor Green
    }
    "down" {
        docker compose @composeArgs down
    }
    "logs" {
        docker compose @composeArgs logs -f
    }
    "ps" {
        docker compose @composeArgs ps
    }
}
