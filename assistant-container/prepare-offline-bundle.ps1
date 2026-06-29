[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BundleDir = Join-Path $ScriptDir "offline-bundle"
$WheelsDir = Join-Path $BundleDir "wheels"
$ModelsDir = Join-Path $BundleDir "models"
$ChromaCacheDir = Join-Path $BundleDir "chroma-cache"
$NextStandalone = Join-Path $BundleDir "next-standalone"
$NextPublic = Join-Path $BundleDir "next-public"
$NextStatic = Join-Path $BundleDir "next-static"

Write-Host "=== Preparing offline bundle for Docker build ===" -ForegroundColor Cyan
Write-Host "Run this script on a machine WITH internet access." -ForegroundColor Yellow
Write-Host "Already downloaded files are skipped (resume-friendly)." -ForegroundColor Yellow
Write-Host ""

# Ensure bundle dirs exist
foreach ($dir in @($BundleDir, $WheelsDir, $ModelsDir, $ChromaCacheDir, $NextStandalone, $NextPublic, $NextStatic)) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

Write-Host ""

function Download-IfMissing {
    param($Url, $Dest, $Label, $MinSize = 1MB)
    if ((Test-Path $Dest) -and ((Get-Item $Dest).Length -ge $MinSize)) {
        Write-Host "      Already exists ($([math]::Round((Get-Item $Dest).Length / 1MB, 1)) MB), skipping" -ForegroundColor Yellow
        return
    }
    $existing = 0
    if (Test-Path $Dest) { $existing = (Get-Item $Dest).Length }
    Write-Host "[*] Downloading $Label..." -ForegroundColor Green
    if ($existing -gt 0) {
        Write-Host "      Resuming from $([math]::Round($existing / 1MB, 1)) MB" -ForegroundColor Yellow
    }
    $maxRetries = 5
    for ($i = 0; $i -lt $maxRetries; $i++) {
        if ($i -gt 0) { Write-Host "      Retry $i..." -ForegroundColor Yellow }
        $resume = if ($existing -gt 0) { @("-C", "$existing") } else { @() }
        $errFile = Join-Path $env:TEMP "curl_err_$([System.IO.Path]::GetRandomFileName()).txt"
        $null = curl.exe -L --connect-timeout 30 --max-time 7200 @resume -o $Dest $Url 2>$errFile
        $exitCode = $LASTEXITCODE
        Remove-Item $errFile -Force -ErrorAction SilentlyContinue
        if ($exitCode -eq 0) {
            $size = (Get-Item $Dest).Length
            Write-Host "      $([math]::Round($size / 1MB, 1)) MB" -ForegroundColor Green
            return
        }
        if ($existing -gt 0 -and (Test-Path $Dest)) {
            $existing = (Get-Item $Dest).Length
        }
    }
    throw "Download failed after $maxRetries retries: $Url"
}

# ── 1/6: Ollama tar.zst archive ────────────────────────────────
$OllamaDest = Join-Path $BundleDir "ollama-linux-amd64.tar.zst"
Download-IfMissing -Url "https://ollama.com/download/ollama-linux-amd64.tar.zst" `
    -Dest $OllamaDest -Label "Ollama archive (Linux amd64, tar.zst)" -MinSize 1GB

# ── 2/6: qwen2.5 GGUF ──────────────────────────────────────────
$GgufDest = Join-Path $ModelsDir "Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
Download-IfMissing -Url "https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf" `
    -Dest $GgufDest -Label "qwen2.5:1.5b GGUF (Q4_K_M)" -MinSize 500MB

# ── 3/6: Modelfile ─────────────────────────────────────────────
$Modelfile = Join-Path $BundleDir "Modelfile"
Write-Host "[3/6] Creating Modelfile..." -ForegroundColor Green
@"
FROM /root/.ollama/models/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf
"@ | Out-File -FilePath $Modelfile -Encoding utf8 -Force
Write-Host "      done" -ForegroundColor Green

# ── 4/6: Python wheels ─────────────────────────────────────────
$wheelCount = (Get-ChildItem $WheelsDir -Filter "*.whl" -ErrorAction SilentlyContinue).Count
if ($wheelCount -gt 0) {
    Write-Host "[4/6] Python wheels already cached ($wheelCount wheels), skipping" -ForegroundColor Yellow
} else {
    Write-Host "[4/6] Downloading Python wheels..." -ForegroundColor Green
    $req = Join-Path $ScriptDir "backend" "requirements.txt"
    pip download --only-binary :all: --dest $WheelsDir -r $req 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "      Some packages have no binary wheel, trying with source..." -ForegroundColor Yellow
        pip download --no-deps --dest $WheelsDir -r $req 2>&1 | Out-Null
    }
    $wheelCount = (Get-ChildItem $WheelsDir -Filter "*.whl").Count
    Write-Host "      $wheelCount wheels" -ForegroundColor Green
}

# ── 5/6: Chromadb ONNX model cache ──────────────────────────────
$cacheFiles = Get-ChildItem $ChromaCacheDir -Recurse -File -ErrorAction SilentlyContinue
$cacheSize = ($cacheFiles | Measure-Object -Property Length -Sum).Sum
if ($cacheSize -gt 1MB) {
    Write-Host "[5/6] Chromadb ONNX model already cached ($([math]::Round($cacheSize / 1MB, 1)) MB), skipping" -ForegroundColor Yellow
} else {
    Write-Host "[5/6] Downloading chromadb ONNX model (all-MiniLM-L6-v2)..." -ForegroundColor Green
    New-Item -ItemType Directory -Path $ChromaCacheDir -Force | Out-Null
    $SavedHome = $env:HOME
    $env:HOME = $BundleDir
    python -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2; ONNXMiniLM_L6_V2()(['test'])" 2>&1 | Out-Null
    $env:HOME = $SavedHome
    # Move from $BundleDir/.cache/chroma to $ChromaCacheDir
    if (Test-Path (Join-Path $BundleDir ".cache\chroma")) {
        Move-Item -Path (Join-Path $BundleDir ".cache\chroma\*") -Destination $ChromaCacheDir -Force
        Remove-Item -Path (Join-Path $BundleDir ".cache") -Recurse -Force
    }
    $cacheFiles = Get-ChildItem $ChromaCacheDir -Recurse -File -ErrorAction SilentlyContinue
    $cacheSize = ($cacheFiles | Measure-Object -Property Length -Sum).Sum
    Write-Host "      $([math]::Round($cacheSize / 1MB, 1)) MB cached" -ForegroundColor Green
}

# ── 6/6: Next.js build ─────────────────────────────────────────
$nextFiles = Get-ChildItem $NextStandalone -Recurse -File -ErrorAction SilentlyContinue
$nextSize = ($nextFiles | Measure-Object -Property Length -Sum).Sum
if ($nextSize -gt 1MB) {
    Write-Host "[6/6] Next.js standalone already built ($([math]::Round($nextSize / 1MB, 1)) MB), skipping" -ForegroundColor Yellow
} else {
    Write-Host "[6/6] Building Next.js (npm install + npm run build)..." -ForegroundColor Green
    Push-Location (Join-Path $ScriptDir "web")
    npm install --no-audit --no-fund 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
    npm run build 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "npm run build failed" }

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
}

# ── Summary ────────────────────────────────────────────────────
Write-Host ""
Write-Host "[v] Bundle ready: $BundleDir" -ForegroundColor Cyan
$total = (Get-ChildItem $BundleDir -Recurse -File | Measure-Object -Property Length -Sum).Sum
Write-Host "    Total size: $([math]::Round($total / 1MB, 1)) MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "Copy 'offline-bundle' to the closed-network machine," -ForegroundColor Yellow
Write-Host "place it next to Dockerfile.offline, then run:" -ForegroundColor Yellow
Write-Host "  docker build -f Dockerfile.offline -t rag-assistant-allinone ." -ForegroundColor Yellow
