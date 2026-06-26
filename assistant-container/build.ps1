$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== Building RAG Assistant Docker Image ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will download ~6 GB of base images and models." -ForegroundColor Yellow
Write-Host "Estimated time: 30-120 minutes depending on connection." -ForegroundColor Yellow
Write-Host ""

$start = Get-Date

docker compose -f (Join-Path $ScriptDir "docker-compose.yml") build

if ($LASTEXITCODE -eq 0) {
    $elapsed = [math]::Round(((Get-Date) - $start).TotalMinutes, 1)
    Write-Host "[v] Build complete in ${elapsed}min!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Start the container:" -ForegroundColor Cyan
    Write-Host "  docker compose up -d" -ForegroundColor White
    Write-Host ""
    Write-Host "Check logs:" -ForegroundColor Cyan
    Write-Host "  docker compose logs -f" -ForegroundColor White
} else {
    Write-Host "[!] Build failed (exit code $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}
