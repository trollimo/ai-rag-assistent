param(
    [switch]$Build,
    [switch]$Run,
    [string[]]$Source,
    [string]$Tag,
    [string]$Config,
    [switch]$UpdateCache
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

$version = if ($Tag) { $Tag } elseif (Test-Path (Join-Path $ProjectRoot "VERSION")) {
    (Get-Content (Join-Path $ProjectRoot "VERSION")).Trim()
} else { "latest" }

$image = "rag-generator"

# ── Build ──────────────────────────────────────────────────────────
if ($Build -or -not $Run) {
    $cacheSrc = Join-Path $ProjectRoot "..\assistant-container\offline-bundle\fastembed-cache"
    $cacheDst = Join-Path $ProjectRoot "fastembed-cache"

    # Copy cache only if missing or -UpdateCache flag is set
    $needCopy = $UpdateCache -or -not (Test-Path $cacheDst)
    if ($needCopy) {
        if (Test-Path $cacheSrc) {
            Write-Host "[*] Copying fastembed cache for offline build..." -ForegroundColor Yellow
            Remove-Item -Path $cacheDst -Recurse -Force -ErrorAction SilentlyContinue
            Copy-Item -Path $cacheSrc -Destination $cacheDst -Recurse
        } else {
            Write-Host "[!] fastembed cache not found at $cacheSrc" -ForegroundColor Red
            Write-Host "    Run .\assistant-container\prepare-offline-bundle.ps1 first" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "[*] Using existing fastembed cache (add -UpdateCache to refresh)" -ForegroundColor Gray
    }

    $dockerArgs = @("build", "--build-context", "fastembed-cache=${cacheDst}")
#     if ($Build) { $dockerArgs += "--no-cache" }
    $dockerArgs += @("-t", "${image}:${version}", "-f", "$ProjectRoot\Dockerfile", "$ProjectRoot")
    Write-Host "=== Building ${image}:${version} ===" -ForegroundColor Cyan
    docker @dockerArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[!] Build failed" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    docker tag "${image}:${version}" "${image}:latest" 2>&1 | Out-Null
    Write-Host "[v] Build complete: ${image}:${version}" -ForegroundColor Green
    Write-Host ""
}

# ── Config ─────────────────────────────────────────────────────────
$configMount = @()
if ($Config) {
    $resolvedConfig = (Resolve-Path $Config -ErrorAction SilentlyContinue).Path
    if (-not $resolvedConfig) {
        Write-Host "[!] Config file not found: $Config" -ForegroundColor Red
        exit 1
    }
    $configMount = @("-v", "${resolvedConfig}:/rag/config/rag-sources.yaml:ro")
    Write-Host "  [config] ${resolvedConfig}" -ForegroundColor Gray
} else {
    Write-Host "  [config] built-in (config/rag-sources.yaml)" -ForegroundColor Gray
}

# ── Run ────────────────────────────────────────────────────────────
if ($Run -or -not $Build) {
    $composeFile = Join-Path $ProjectRoot "docker-compose.yml"

    $dockerArgs = @("run", "--rm") + $configMount

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
