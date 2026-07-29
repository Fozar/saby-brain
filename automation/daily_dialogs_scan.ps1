$ErrorActionPreference = 'Continue'

$repoRoot = "C:\Users\aa.timoshenko\PycharmProjects\claude-obsidian"
$promptFile = Join-Path $repoRoot "automation\daily_dialogs_scan_prompt.md"
$logFile = Join-Path $repoRoot "automation\logs\daily_dialogs_scan.log"
$claudeExe = "C:\Users\aa.timoshenko\.local\bin\claude.exe"

Set-Location $repoRoot

$prompt = Get-Content -Raw -Encoding UTF8 $promptFile
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"

"[$timestamp] --- run start ---" | Out-File -FilePath $logFile -Append -Encoding UTF8

try {
    & $claudeExe -p $prompt --dangerously-skip-permissions 2>&1 | Out-File -FilePath $logFile -Append -Encoding UTF8
} catch {
    "[$timestamp] ERROR launching claude: $_" | Out-File -FilePath $logFile -Append -Encoding UTF8
}

"[$timestamp] --- run end ---" | Out-File -FilePath $logFile -Append -Encoding UTF8
