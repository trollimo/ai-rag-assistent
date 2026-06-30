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

if ($Build) {
    Write-Host "=== Building RAG Assistant Docker Image ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "This will download ~6 GB of base images and models." -ForegroundColor Yellow
    Write-Host "Estimated time: 30-120 minutes depending on connection." -ForegroundColor Yellow
    Write-Host ""
    $start = Get-Date
    docker compose -f $ComposeFile build --no-cache
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] Build failed (exit code $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    $elapsed = [math]::Round(((Get-Date) - $start).TotalMinutes, 1)
    Write-Host "[v] Build complete in ${elapsed}min!" -ForegroundColor Green
    Write-Host ""
}

docker compose -f $ComposeFile up -d

Write-Host ""
Write-Host "[v] RAG Assistant is running!" -ForegroundColor Green
Write-Host ""
Write-Host "  Web UI: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  API:    http://localhost:8000" -ForegroundColor Cyan
Write-Host "  MCP:    http://localhost:9081/sse" -ForegroundColor Cyan
Write-Host ""

if ($Logs) { docker compose -f $ComposeFile logs -f }
