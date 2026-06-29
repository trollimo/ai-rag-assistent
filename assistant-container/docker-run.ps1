param(
    [switch]$Build,
    [switch]$Logs,
    [switch]$Stop,
    [switch]$Restart
)

$ErrorActionPreference = "Stop"
$ComposeFile = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "docker-compose.yml"

if ($Stop)    { docker compose -f $ComposeFile down; exit }
if ($Restart) { docker compose -f $ComposeFile restart; exit }
if ($Build)   { docker compose -f $ComposeFile build --no-cache }

docker compose -f $ComposeFile up -d

Write-Host ""
Write-Host "[v] RAG Assistant is running!" -ForegroundColor Green
Write-Host ""
Write-Host "  Web UI: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  API:    http://localhost:8000" -ForegroundColor Cyan
Write-Host "  MCP:    http://localhost:9081/sse" -ForegroundColor Cyan
Write-Host ""

if ($Logs) { docker compose -f $ComposeFile logs -f }
