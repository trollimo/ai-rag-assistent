param([string]$Question = "Какие правила хоровода?")

$ok=0; $bad=0

function Check($Name, $Body) {
    try { $r = & $Body; Write-Host "  [PASS] $Name" -ForegroundColor Green; $global:ok++; return $r }
    catch { Write-Host "  [FAIL] $Name - $_" -ForegroundColor Red; $global:bad++; return $null }
}

Write-Host "=== RAG Assistant: Smoke Tests ===" -ForegroundColor Cyan
Write-Host "Question: $Question`n" -ForegroundColor Gray

Write-Host "[1] Health checks" -ForegroundColor Yellow
Check "GET / (FastAPI)" { (curl.exe -s "http://localhost:8000/" | ConvertFrom-Json).status }
Check "Web UI" { if ((curl.exe -s "http://localhost:3000/") -match "RAG Assistant") { $true } else { throw "not found" } }

Write-Host "`n[2] LLM direct (port 9080)" -ForegroundColor Yellow
$body = @{model="qwen2.5"; messages=@(@{role="user"; content=$Question}); stream=$false} | ConvertTo-Json
Set-Content "$env:TEMP\ragt.json" -Value $body -Encoding UTF8
$ans = Check "POST /v1/chat/completions" {
    $r = curl.exe -s "http://localhost:9080/v1/chat/completions" -H "Content-Type: application/json" -d "@$env:TEMP\ragt.json" | ConvertFrom-Json
    $r.choices[0].message.content
}
if ($ans) { Write-Host "  --> $($ans.Substring(0, [Math]::Min(120, $ans.Length)))..." -ForegroundColor DarkGray }

Write-Host "`n[3] RAG chat (port 8000/chat)" -ForegroundColor Yellow
$body2 = @{question=$Question} | ConvertTo-Json
Set-Content "$env:TEMP\ragc.json" -Value $body2 -Encoding UTF8
$rag = Check "POST /chat" {
    $r = curl.exe -s "http://localhost:8000/chat" -H "Content-Type: application/json" -d "@$env:TEMP\ragc.json" | ConvertFrom-Json
    if (-not $r.answer) { throw "Empty answer" }; $r
}
if ($rag) {
    Write-Host "  --> $($rag.answer.Substring(0, [Math]::Min(120, $rag.answer.Length)))..." -ForegroundColor DarkGray
    Write-Host "  --> sources: $($rag.sources.count)" -ForegroundColor DarkGray
}

Remove-Item "$env:TEMP\ragt.json","$env:TEMP\ragc.json" -Force -ErrorAction SilentlyContinue
Write-Host "`n=== $ok passed, $bad failed ===" -ForegroundColor $(if ($bad -eq 0) { "Green" } else { "Red" })
exit $(if ($bad -eq 0) { 0 } else { 1 })
