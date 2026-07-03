$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

$DbPath = Join-Path $ProjectRoot "output\chroma_db"
$DbContainer = "/rag/output/chroma_db"
$Image = "rag-generator:latest"

Write-Host "Running inspect in Docker ($Image) ..." -ForegroundColor Cyan

$query = ""
if ($args.Count -ge 1) {
    $query = $args[0]
}

# Resolve to absolute path for Docker mount
$DbAbs = (Resolve-Path $DbPath).Path

if ($query) {
    docker run --rm -v "${DbAbs}:$DbContainer" $Image python src/inspect/browse_db.py $DbContainer "knowledge_base" $query
} else {
    docker run --rm -v "${DbAbs}:$DbContainer" $Image python src/inspect/browse_db.py $DbContainer "knowledge_base"
}
