[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BundleDir = Join-Path $ScriptDir "offline-bundle"
$WheelsDir = Join-Path $BundleDir "wheels"
$ModelsDir = Join-Path $BundleDir "models"
$ChromaCacheDir = Join-Path $BundleDir "chroma-cache"
$FastembedCacheDir = Join-Path $BundleDir "fastembed-cache"
$NextStandalone = Join-Path $BundleDir "next-standalone"
$NextPublic = Join-Path $BundleDir "next-public"
$NextStatic = Join-Path $BundleDir "next-static"

Write-Host "=== Preparing offline bundle for Docker build ===" -ForegroundColor Cyan
Write-Host "Run this script on a machine WITH internet access." -ForegroundColor Yellow
Write-Host "Already downloaded files are skipped (resume-friendly)." -ForegroundColor Yellow
Write-Host ""

# Ensure bundle dirs exist
foreach ($dir in @($BundleDir, $WheelsDir, $ModelsDir, $ChromaCacheDir, $FastembedCacheDir, $NextStandalone, $NextPublic, $NextStatic)) {
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
# $OllamaDest = Join-Path $BundleDir "ollama-linux-amd64.tar.zst"
# Download-IfMissing -Url "https://ollama.com/download/ollama-linux-amd64.tar.zst" `
#     -Dest $OllamaDest -Label "Ollama archive (Linux amd64, tar.zst)" -MinSize 1GB

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
$req = Join-Path $ScriptDir "backend/requirements.txt"
$wheels = Get-ChildItem $WheelsDir -Filter "*.whl" -ErrorAction SilentlyContinue
$wheelCount = $wheels.Count
# Re-download when requirements.txt is newer than the cache. A plain "skip if
# not empty" check silently kept an outdated wheel set: adding a dependency
# left it missing offline, and the Docker build quietly reached PyPI instead
# (which only works on a machine with internet -- exactly what this bundle
# exists to avoid needing).
$reqNewer = $false
if ($wheelCount -gt 0 -and (Test-Path $req)) {
    $newestWheel = ($wheels | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
    $reqNewer = (Get-Item $req).LastWriteTime -gt $newestWheel
}
# A non-Linux wheel in the cache is proof the cache itself is invalid, whatever
# the timestamps say -- the image is Linux, so these can never be installed.
# Checked outside the skip branch on purpose: the timestamp heuristic only
# catches "requirements changed", never "what we downloaded was wrong".
$badWheels = $wheels | Where-Object { $_.Name -match "-(win_amd64|win32|macosx[^-]*)\.whl$" }
if ($badWheels) {
    Write-Host "[4/6] Cache has $($badWheels.Count) non-Linux wheel(s) -- rebuilding it" -ForegroundColor Yellow
}
if ($wheelCount -gt 0 -and -not $reqNewer -and -not $badWheels) {
    Write-Host "[4/6] Python wheels already cached ($wheelCount wheels), skipping" -ForegroundColor Yellow
} else {
    if ($reqNewer) {
        Write-Host "[4/6] requirements.txt newer than wheel cache -- refreshing" -ForegroundColor Yellow
    }
    Write-Host "[4/6] Downloading Python wheels (linux x86_64)..." -ForegroundColor Green
    # Several manylinux tags on purpose. onnxruntime (via fastembed) ships no
    # manylinux2014 wheel, so asking for that tag alone makes the whole
    # resolution fail -- and the old fallback (`pip download --no-deps`, with
    # no --platform at all) then quietly filled the bundle with *Windows*
    # wheels, which are useless in the Linux image. That went unnoticed because
    # the Docker build has internet and silently pulled the real ones from
    # PyPI; on a closed network it would simply not build.
    if ($badWheels) {
        Write-Host "      Removing $($badWheels.Count) non-Linux wheel(s) from cache" -ForegroundColor Yellow
        $badWheels | Remove-Item -Force
    }
    pip download --only-binary :all: `
        --platform manylinux2014_x86_64 `
        --platform manylinux_2_17_x86_64 `
        --platform manylinux_2_28_x86_64 `
        --python-version 3.11 `
        --dest $WheelsDir -r $req 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "pip download failed -- the offline bundle would be incomplete. Run the command manually to see the resolver error."
    }
    $wheelCount = (Get-ChildItem $WheelsDir -Filter "*.whl").Count
    Write-Host "      $wheelCount wheels" -ForegroundColor Green
}

# ── 6/7: Fastembed model cache ──────────────────────────────────
$feCacheFiles = Get-ChildItem $FastembedCacheDir -Recurse -File -ErrorAction SilentlyContinue
$feCacheSize = ($feCacheFiles | Measure-Object -Property Length -Sum).Sum
if ($feCacheSize -gt 1MB) {
    Write-Host "[6/7] Fastembed model already cached ($([math]::Round($feCacheSize / 1MB, 1)) MB), skipping" -ForegroundColor Yellow
} else {
    Write-Host "[6/7] Downloading fastembed model (multilingual-e5-large)..." -ForegroundColor Green
    New-Item -ItemType Directory -Path $FastembedCacheDir -Force | Out-Null
    python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='intfloat/multilingual-e5-large').embed(['test'])"
    # Windows cache (LOCALAPPDATA\Temp) vs Linux cache (~/.cache)
    $possibleCaches = @(
        (Join-Path $env:LOCALAPPDATA "Temp\fastembed_cache"),
        (Join-Path $env:USERPROFILE ".cache\fastembed")
    )
    $SourceFe = $null
    foreach ($p in $possibleCaches) {
        if (Test-Path $p) { $SourceFe = $p; break }
    }
    if ($SourceFe) {
        Write-Host "      Copying from $SourceFe" -ForegroundColor Gray
        Copy-Item -Path "$SourceFe\*" -Destination $FastembedCacheDir -Recurse -Force
    }
    $feCacheFiles = Get-ChildItem $FastembedCacheDir -Recurse -File -ErrorAction SilentlyContinue
    $feCacheSize = ($feCacheFiles | Measure-Object -Property Length -Sum).Sum
    Write-Host "      $([math]::Round($feCacheSize / 1MB, 1)) MB cached" -ForegroundColor Green
}

# ── 7/7: Next.js build ─────────────────────────────────────────
# Always rebuilt (unlike the download steps above) -- it's a local build of
# fast-changing source, not an expensive network fetch, so there is no safe
# way to tell "already built" apart from "built from stale source" without
# hashing the web/ tree. A stale skip here silently served old UI code
# through multiple Docker rebuilds before this was caught.
Write-Host "[6/6] Building Next.js (npm install + npm run build)..." -ForegroundColor Green
Push-Location (Join-Path $ScriptDir "web")
npm install --no-audit --no-fund 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
npm run build 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { throw "npm run build failed" }

Remove-Item (Join-Path $NextStandalone "*") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $NextPublic "*") -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $NextStatic "*") -Recurse -Force -ErrorAction SilentlyContinue
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
