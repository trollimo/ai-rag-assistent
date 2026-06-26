$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BundleDir = Join-Path $ScriptDir "offline-bundle"
$WheelsDir = Join-Path $BundleDir "wheels"
$HfCacheDir = Join-Path $BundleDir "hf-cache"
$NpmCacheDir = Join-Path $BundleDir "npm-cache"

Write-Host "=== Preparing offline bundle for Docker build ===" -ForegroundColor Cyan
Write-Host "Run this script on a machine WITH internet access." -ForegroundColor Yellow
Write-Host "Then copy the '$BundleDir' folder to the closed-network machine." -ForegroundColor Yellow
Write-Host ""

# --- Python wheels ---
$req = Join-Path $ScriptDir "backend" "requirements.txt"
if (Test-Path $req) {
    New-Item -ItemType Directory -Path $WheelsDir -Force | Out-Null
    Write-Host "[1/3] Downloading Python wheels..." -ForegroundColor Green
    pip3 download --no-cache-dir --only-binary :all: --dest $WheelsDir -r $req
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    Some packages have no binary wheel, trying with source..." -ForegroundColor Yellow
        pip3 download --no-cache-dir --dest $WheelsDir -r $req
        if ($LASTEXITCODE -ne 0) { throw "pip download failed" }
    }
    Write-Host "      $((Get-ChildItem $WheelsDir).Count) wheels saved" -ForegroundColor Green
} else {
    Write-Host "[!] requirements.txt not found at $req" -ForegroundColor Red
    exit 1
}

# --- HuggingFace model cache (sentence-transformers/all-MiniLM-L6-v2) ---
Write-Host "[2/3] Downloading HuggingFace model (all-MiniLM-L6-v2)..." -ForegroundColor Green
$env:HF_HOME = $HfCacheDir
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
if ($LASTEXITCODE -ne 0) { throw "HF model download failed" }
$hfSize = (Get-ChildItem $HfCacheDir -Recurse -File | Measure-Object -Property Length -Sum).Sum
Write-Host "      HF cache: $([math]::Round($hfSize / 1MB, 1)) MB" -ForegroundColor Green

# --- NPM packages ---
$pkgJson = Join-Path $ScriptDir "web" "package.json"
if (Test-Path $pkgJson) {
    New-Item -ItemType Directory -Path $NpmCacheDir -Force | Out-Null
    Write-Host "[3/3] Preparing npm offline cache..." -ForegroundColor Green
    Push-Location (Join-Path $ScriptDir "web")
    npm install --no-audit --no-fund --cache $NpmCacheDir
    if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
    Copy-Item -Path "node_modules" -Destination (Join-Path $BundleDir "node_modules") -Recurse -Force
    Pop-Location
    Write-Host "      node_modules saved" -ForegroundColor Green
} else {
    Write-Host "[!] package.json not found at $pkgJson" -ForegroundColor Red
    exit 1
}

# --- Summary ---
$size = (Get-ChildItem $BundleDir -Recurse -File | Measure-Object -Property Length -Sum).Sum
Write-Host ""
Write-Host "[v] Bundle ready: $BundleDir" -ForegroundColor Cyan
Write-Host "    Size: $([math]::Round($size / 1MB, 1)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "Copy '$BundleDir' to the closed-network machine," -ForegroundColor Yellow
Write-Host "place it next to Dockerfile, then run 'docker compose build'." -ForegroundColor Yellow
