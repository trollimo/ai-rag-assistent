param(
    [switch]$Build,
    [switch]$Logs,
    [switch]$Stop,
    [switch]$Restart
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ComposeFile = Join-Path $ScriptDir "docker-compose.yml"

if ($Stop) {
    Write-Host "=== Stopping RAG Assistant ===" -ForegroundColor Cyan
    docker compose -f $ComposeFile down
    Write-Host "[v] Stopped" -ForegroundColor Green
    exit 0
}

if ($Restart) {
    Write-Host "=== Restarting RAG Assistant ===" -ForegroundColor Cyan
    docker compose -f $ComposeFile restart
    Write-Host "[v] Restarted" -ForegroundColor Green
    exit 0
}

$BundlePath = Join-Path $ScriptDir "offline-bundle"
$HasBundle = Test-Path (Join-Path $BundlePath "models")

if (-not $HasBundle) {
    Write-Host "=== Building RAG Assistant (no offline-bundle found) ===" -ForegroundColor Yellow
    Write-Host "This will download ~6 GB of base images." -ForegroundColor Yellow
    Write-Host "For offline build, prepare bundle first:" -ForegroundColor Yellow
    Write-Host "  .\assistant-container\prepare-offline-bundle.ps1" -ForegroundColor White
    Write-Host ""

    $start = Get-Date
    docker compose -f $ComposeFile build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] Build failed" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    $elapsed = [math]::Round(((Get-Date) - $start).TotalMinutes, 1)
    Write-Host "[v] Build complete in ${elapsed}min" -ForegroundColor Green
    Write-Host ""
}

if ($Build) {
    Write-Host "=== Rebuilding RAG Assistant ===" -ForegroundColor Cyan
    $start = Get-Date
    docker compose -f $ComposeFile build --no-cache
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] Build failed" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    $elapsed = [math]::Round(((Get-Date) - $start).TotalMinutes, 1)
    Write-Host "[v] Rebuild complete in ${elapsed}min" -ForegroundColor Green
    Write-Host ""
}

Write-Host "=== Starting RAG Assistant ===" -ForegroundColor Cyan
Write-Host ""

docker compose -f $ComposeFile up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Failed to start" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "Waiting for services..." -ForegroundColor Gray
Start-Sleep -Seconds 8

$services = @(
    @{ Name = "llama-server (LLM)"; Port = 8080; Path = "/" },
    @{ Name = "FastAPI (RAG)";     Port = 8000; Path = "/" },
    @{ Name = "Web UI";           Port = 3000; Path = "/" }
)

foreach ($svc in $services) {
    try {
        $r = curl.exe -s --max-time 3 "http://localhost:$($svc.Port)$($svc.Path)" 2>$null
        if ($r) { Write-Host "  [PASS] $($svc.Name) :$($svc.Port)" -ForegroundColor Green }
        else { Write-Host "  [SKIP] $($svc.Name) :$($svc.Port) (no response)" -ForegroundColor Yellow }
    } catch {
        Write-Host "  [SKIP] $($svc.Name) :$($svc.Port) (not ready)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[v] RAG Assistant is running!" -ForegroundColor Green
Write-Host ""
Write-Host "  Web UI: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  API:    http://localhost:8000" -ForegroundColor Cyan
Write-Host "  MCP:    http://localhost:8001/sse" -ForegroundColor Cyan
Write-Host ""
Write-Host "Commands:" -ForegroundColor Gray
Write-Host "  .\assistant-container\docker-run.ps1 -Logs    tail logs" -ForegroundColor White
Write-Host "  .\assistant-container\docker-run.ps1 -Stop    stop container" -ForegroundColor White
Write-Host "  .\assistant-container\docker-run.ps1 -Restart restart container" -ForegroundColor White
Write-Host "  .\assistant-container\docker-run.ps1 -Build   rebuild from scratch" -ForegroundColor White

if ($Logs) {
    docker compose -f $ComposeFile logs -f
}