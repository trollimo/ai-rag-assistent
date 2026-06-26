$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

$DbPath = Join-Path $ProjectRoot "output\chroma_db"
$PyScript = Join-Path $ScriptDir "browse_db.py"

if ($args.Count -ge 1) {
    python $PyScript $DbPath "knowledge_base" $args[0]
} else {
    python $PyScript $DbPath "knowledge_base"
}
