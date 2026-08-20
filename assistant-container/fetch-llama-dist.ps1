# Downloads the llama.cpp release archive into offline-bundle so image builds
# need no network. Run once on a machine WITH internet; the bundle then travels
# to the closed network together with the GGUF model.
#
# The archive is kept packed on purpose: it contains Linux symlinks
# (libggml.so -> libggml.so.0) that Windows cannot recreate. Dockerfile.llm
# unpacks it inside the Linux image, where symlinks work.
param(
    [string]$Version = "b9804",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$dest = Join-Path $root "offline-bundle\llama"
$archive = Join-Path $dest "llama-dist.tar.gz"

if ((Test-Path $archive) -and -not $Force) {
    $mb = (Get-Item $archive).Length / 1MB
    Write-Host ("[*] Archive already present ({0:N0} MB), use -Force to refresh" -f $mb) -ForegroundColor Gray
    exit 0
}

$url = "https://github.com/ggml-org/llama.cpp/releases/download/$Version/llama-$Version-bin-ubuntu-x64.tar.gz"

New-Item -ItemType Directory -Force $dest | Out-Null
Write-Host "[*] Downloading llama.cpp $Version ..." -ForegroundColor Cyan
Invoke-WebRequest -Uri $url -OutFile $archive -UseBasicParsing

# Record which build this is, so the image and the bundle cannot silently diverge
Set-Content -Path (Join-Path $dest "VERSION") -Value $Version -Encoding utf8

$mb = (Get-Item $archive).Length / 1MB
Write-Host ("[v] llama dist ready: {0} ({1:N0} MB)" -f $archive, $mb) -ForegroundColor Green
