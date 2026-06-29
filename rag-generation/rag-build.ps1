param(
    [switch]$Rebuild
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

$version = if (Test-Path (Join-Path $ProjectRoot "VERSION")) {
    (Get-Content (Join-Path $ProjectRoot "VERSION")).Trim()
} else { "latest" }

$image = "rag-generator"

if ($Rebuild) {
    Write-Host "=== Rebuilding ${image}:${version} (no-cache) ===" -ForegroundColor Cyan
    docker build --no-cache -t "${image}:${version}" -f "$ProjectRoot\Dockerfile" "$ProjectRoot"
} else {
    Write-Host "=== Building ${image}:${version} ===" -ForegroundColor Cyan
    docker build -t "${image}:${version}" -f "$ProjectRoot\Dockerfile" "$ProjectRoot"
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "[!] Build failed" -ForegroundColor Red
    exit $LASTEXITCODE
}

docker tag "${image}:${version}" "${image}:latest" 2>&1 | Out-Null

Write-Host ""
Write-Host "[v] Done!" -ForegroundColor Green
Write-Host "  Image: ${image}:${version}"
Write-Host ""
Write-Host "Run with:"
Write-Host "  docker run --rm -v ${ProjectRoot}\output:/rag/output ${image}:${version}"
