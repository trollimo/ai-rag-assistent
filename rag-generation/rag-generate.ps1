$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== RAG Generation ===" -ForegroundColor Cyan
Write-Host ""

# ── Prerequisites check ─────────────────────────────────────────────
$missing = @()
$required = @(
    @{ Name = "Python";     Check = { python --version 2>&1 | Out-Null } },
    @{ Name = "Git";        Check = { git --version 2>&1 | Out-Null } },
    @{ Name = "PowerShell"; Check = { $PSVersionTable.PSVersion -ge [Version]"5.1" } }
)

foreach ($req in $required) {
    $ok = & $req.Check
    if (-not $?) {
        $missing += $req.Name
    }
}

if ($missing.Count -gt 0) {
    Write-Host "[!] Missing prerequisites:" -ForegroundColor Red
    foreach ($m in $missing) {
        Write-Host "    - $m" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Install missing tools and try again." -ForegroundColor Red
    exit 1
}

Write-Host "[v] All prerequisites found" -ForegroundColor Green

# ── Virtual env ─────────────────────────────────────────────────────
$VenvDir = Join-Path $ProjectRoot ".venv"
if (-not (Test-Path $VenvDir)) {
    Write-Host "[*] Creating virtual environment ..." -ForegroundColor Yellow
    python -m venv $VenvDir
}

& "$VenvDir\Scripts\Activate.ps1"

# ── Dependencies ────────────────────────────────────────────────────
Write-Host "[*] Installing dependencies ..." -ForegroundColor Yellow
pip install -r (Join-Path $ProjectRoot "requirements.txt") --quiet

# ── Run ─────────────────────────────────────────────────────────────
Write-Host "[*] Running ingest ..." -ForegroundColor Cyan
python (Join-Path $ProjectRoot "src" "ingest.py")
$exitCode = $LASTEXITCODE

deactivate

if ($exitCode -eq 0) {
    Write-Host "[v] RAG Generation Complete!" -ForegroundColor Green
} else {
    Write-Host "[!] RAG Generation failed (exit code $exitCode)" -ForegroundColor Red
    exit $exitCode
}
