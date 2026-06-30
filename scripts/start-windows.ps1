$ErrorActionPreference = "Stop"

$Root = Split-Path -Path $PSScriptRoot -Parent
Set-Location $Root

docker compose up --build -d
docker compose ps
Write-Output "App is running at http://localhost:8000"
