param(
    [switch]$Build,
    [switch]$Run,
    [string[]]$Source,
    [string]$Tag
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

$version = if ($Tag) { $Tag } elseif (Test-Path (Join-Path $ProjectRoot "VERSION")) {
    (Get-Content (Join-Path $ProjectRoot "VERSION")).Trim()
} else { "latest" }

$image = "rag-generator"

# ── Build ──────────────────────────────────────────────────────────
if ($Build -or -not $Run) {
    $cache = if ($Build) { @("--no-cache") } else { @() }
    Write-Host "=== Building ${image}:${version} ===" -ForegroundColor Cyan
    docker build @cache -t "${image}:${version}" -f "$ProjectRoot\Dockerfile" "$ProjectRoot"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] Build failed" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    docker tag "${image}:${version}" "${image}:latest" 2>&1 | Out-Null
    Write-Host "[v] Build complete: ${image}:${version}" -ForegroundColor Green
    Write-Host ""
}

# ── Run ────────────────────────────────────────────────────────────
if ($Run -or -not $Build) {
    $composeFile = Join-Path $ProjectRoot "docker-compose.yml"

    $dockerArgs = @("run", "--rm")

    if ($Source) {
        $idx = 0
        foreach ($s in $Source) {
            $resolved = (Resolve-Path $s -ErrorAction SilentlyContinue).Path
            if (-not $resolved) {
                Write-Host "[!] Source dir not found: $s" -ForegroundColor Red
                exit 1
            }
            $mount = "/external/src$idx"
            $dockerArgs += "-v"; $dockerArgs += "${resolved}:${mount}:ro"
            $dockerArgs += "-e"; $dockerArgs += "RAG_SRC${idx}=${mount}"
            Write-Host "  [src${idx}] ${resolved} -> ${mount}" -ForegroundColor Gray
            $idx++
        }
    }

    $dockerArgs += "generator"

    Write-Host "=== Running RAG Generator ===" -ForegroundColor Cyan
    Write-Host ""

    docker compose -f $composeFile @dockerArgs

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] Generation failed (exit $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }

    Write-Host ""
    Write-Host "[v] RAG Generation complete!" -ForegroundColor Green
    Write-Host "  Output: $ProjectRoot\output\chroma_db" -ForegroundColor Cyan
}
