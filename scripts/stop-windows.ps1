$ErrorActionPreference = "Stop"

$Root = Split-Path -Path $PSScriptRoot -Parent
Set-Location $Root

docker compose down --remove-orphans
Write-Output "App stopped."
