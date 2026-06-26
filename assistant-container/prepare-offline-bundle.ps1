$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BundleDir = Join-Path $ScriptDir "offline-bundle"
$WheelsDir = Join-Path $BundleDir "wheels"
$ModelsDir = Join-Path $BundleDir "models"
$FastembedCache = Join-Path $BundleDir "fastembed-cache"
$NextStandalone = Join-Path $BundleDir "next-standalone"
$NextPublic = Join-Path $BundleDir "next-public"
$NextStatic = Join-Path $BundleDir "next-static"

Write-Host "=== Preparing offline bundle for Docker build ===" -ForegroundColor Cyan
Write-Host "Run this script on a machine WITH internet access." -ForegroundColor Yellow
Write-Host "Then copy the 'offline-bundle' folder to the closed-network machine." -ForegroundColor Yellow
Write-Host ""

# Clean and create bundle dirs
if (Test-Path $BundleDir) { Remove-Item -Recurse -Force $BundleDir }
foreach ($dir in @($BundleDir, $WheelsDir, $ModelsDir, $FastembedCache, $NextStandalone, $NextPublic, $NextStatic)) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

Write-Host ""

# ── 1/6: Ollama tar.zst archive ────────────────────────────────
Write-Host "[1/6] Downloading Ollama archive (Linux amd64, tar.zst)..." -ForegroundColor Green
$OllamaUrl = "https://ollama.com/download/ollama-linux-amd64.tar.zst"
$OllamaDest = Join-Path $BundleDir "ollama-linux-amd64.tar.zst"
Invoke-WebRequest -Uri $OllamaUrl -OutFile $OllamaDest -UseBasicParsing
$size = (Get-Item $OllamaDest).Length
Write-Host "      $([math]::Round($size / 1MB, 1)) MB" -ForegroundColor Green

# ── 2/6: qwen2.5 GGUF ──────────────────────────────────────────
Write-Host "[2/6] Downloading qwen2.5:1.5b GGUF (Q4_K_M)..." -ForegroundColor Green
$GgufUrl = "https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
$GgufDest = Join-Path $ModelsDir "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
Invoke-WebRequest -Uri $GgufUrl -OutFile $GgufDest -UseBasicParsing
$size = (Get-Item $GgufDest).Length
Write-Host "      $([math]::Round($size / 1MB, 1)) MB" -ForegroundColor Green

# ── 3/6: Modelfile ─────────────────────────────────────────────
Write-Host "[3/6] Creating Modelfile..." -ForegroundColor Green
$Modelfile = Join-Path $BundleDir "Modelfile"
@"
FROM /root/.ollama/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf
"@ | Out-File -FilePath $Modelfile -Encoding utf8

# ── 4/6: Python wheels ─────────────────────────────────────────
Write-Host "[4/6] Downloading Python wheels..." -ForegroundColor Green
$req = Join-Path $ScriptDir "backend" "requirements.txt"
pip download --only-binary :all: --dest $WheelsDir -r $req 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "      Some packages have no binary wheel, trying with source..." -ForegroundColor Yellow
    pip download --no-deps --dest $WheelsDir -r $req 2>&1 | Out-Null
}
$wheelCount = (Get-ChildItem $WheelsDir -Filter "*.whl").Count
Write-Host "      $wheelCount wheels" -ForegroundColor Green

# ── 5/6: Fastembed model cache ──────────────────────────────────
Write-Host "[5/6] Downloading fastembed model (all-MiniLM-L6-v2)..." -ForegroundColor Green
$env:FASTEMBED_CACHE_DIR = $FastembedCache
python -c "from chromadb.utils.embedding_functions import FastEmbedEmbeddingFunction; FastEmbedEmbeddingFunction('all-MiniLM-L6-v2')" 2>&1 | Out-Null
$cacheSize = (Get-ChildItem $FastembedCache -Recurse -File | Measure-Object -Property Length -Sum).Sum
Write-Host "      $([math]::Round($cacheSize / 1MB, 1)) MB cached" -ForegroundColor Green

# ── 6/6: Next.js build ─────────────────────────────────────────
Write-Host "[6/6] Building Next.js (npm install + npm run build)..." -ForegroundColor Green
Push-Location (Join-Path $ScriptDir "web")
npm install --no-audit --no-fund 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
npm run build 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { throw "npm run build failed" }

# Copy standalone output
if (Test-Path ".next/standalone") {
    Copy-Item -Path ".next/standalone/*" -Destination $NextStandalone -Recurse -Force
}
if (Test-Path "public") {
    Copy-Item -Path "public/*" -Destination $NextPublic -Recurse -Force
}
if (Test-Path ".next/static") {
    Copy-Item -Path ".next/static/*" -Destination $NextStatic -Recurse -Force
}
Pop-Location
Write-Host "      Next.js standalone saved" -ForegroundColor Green

# ── Summary ────────────────────────────────────────────────────
Write-Host ""
Write-Host "[v] Bundle ready: $BundleDir" -ForegroundColor Cyan
$total = (Get-ChildItem $BundleDir -Recurse -File | Measure-Object -Property Length -Sum).Sum
Write-Host "    Total size: $([math]::Round($total / 1MB, 1)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "Copy 'offline-bundle' to the closed-network machine," -ForegroundColor Yellow
Write-Host "place it next to Dockerfile.offline, then run:" -ForegroundColor Yellow
Write-Host "  docker build -f Dockerfile.offline -t rag-assistant-allinone ." -ForegroundColor Yellow
Write-Host ""
