param(
    [switch]$Build,
    [switch]$NoCache,
    [switch]$Stop,
    [switch]$Rerun,
    [switch]$Logs,
    [string]$Service   # limit to "assistant" or "llm"; omit for both
)

$ErrorActionPreference = "Stop"
$ComposeFile = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "docker-compose.yml"
$svcArgs = if ($Service) { @($Service) } else { @() }

if ($Stop) {
    Write-Host "=== Stopping ===" -ForegroundColor Cyan
    docker compose -f $ComposeFile down
    exit $LASTEXITCODE
}

# Recreates containers instead of `docker compose restart`: restart reuses
# whatever env vars were baked in when the container was first created and
# does NOT re-read docker-compose.yml / .env -- editing LLM_BASE_URL (or
# anything else) and running `restart` silently keeps serving the old value.
# down+up is what actually picks up compose/.env changes.
if ($Rerun) {
    Write-Host "=== Rerun (recreating containers, picks up compose/.env changes) ===" -ForegroundColor Cyan
    docker compose -f $ComposeFile down @svcArgs
    docker compose -f $ComposeFile up -d @svcArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "[v] Rerun complete" -ForegroundColor Green
    exit 0
}

if ($Build) {
    Write-Host "=== Building ===" -ForegroundColor Cyan
    if ($NoCache) {
        Write-Host "[!] -NoCache: ignoring layer cache -- this re-fetches the ~2 GB" -ForegroundColor Yellow
        Write-Host "    fastembed-cache context and reinstalls pip even though" -ForegroundColor Yellow
        Write-Host "    nothing in those layers changed. Expect several minutes." -ForegroundColor Yellow
    }
    $start = Get-Date
    $buildArgs = @("build")
    if ($NoCache) { $buildArgs += "--no-cache" }
    $buildArgs += $svcArgs
    docker compose -f $ComposeFile @buildArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] Build failed (exit code $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    $elapsed = [math]::Round(((Get-Date) - $start).TotalMinutes, 1)
    Write-Host "[v] Build complete in ${elapsed}min" -ForegroundColor Green
    Write-Host ""
    Write-Host "    Built image(s) are tagged :latest only. To also tag a version" -ForegroundColor Gray
    Write-Host "    number (bump assistant-container/VERSION first):" -ForegroundColor Gray
    Write-Host "      docker tag rag-offline:latest rag-offline:<version>" -ForegroundColor Gray
    Write-Host "      docker tag rag-llm:latest rag-llm:<version>" -ForegroundColor Gray
    Write-Host "    ...then update the image: tags in docker-compose.yml to match." -ForegroundColor Gray
    Write-Host ""
}

docker compose -f $ComposeFile up -d @svcArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "[v] Running" -ForegroundColor Green
Write-Host ""
Write-Host "  Web UI: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  API:    http://localhost:8000" -ForegroundColor Cyan
Write-Host "  MCP:    http://localhost:9081/mcp (streamable-http) + /sse" -ForegroundColor Cyan
Write-Host "  LLM:    http://localhost:9080/v1/chat/completions" -ForegroundColor Cyan
Write-Host ""

if ($Logs) { docker compose -f $ComposeFile logs -f @svcArgs }
