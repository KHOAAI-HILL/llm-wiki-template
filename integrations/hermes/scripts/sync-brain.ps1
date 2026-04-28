# Sync Second Brain wiki from GitHub (Windows)
# Usage: Called by Hermes cron via sync_brain.py wrapper or scheduled task

$ErrorActionPreference = "Stop"

$HermesHome = $env:HERMES_HOME
if ([string]::IsNullOrWhiteSpace($HermesHome)) {
    $HermesHome = "$env:USERPROFILE\.hermes"
}

$BrainDir = Join-Path $HermesHome "second-brain"

if (-Not (Test-Path (Join-Path $BrainDir ".git"))) {
    Write-Error "ERROR: Not a git repo at $BrainDir"
    exit 1
}

Set-Location $BrainDir

try {
    git fetch origin 2>&1 | Write-Host
    git reset --hard origin/main 2>&1 | Write-Host
    $Timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    Write-Host "Synced at $Timestamp"
    
    $ArticleCount = (Get-ChildItem -Path "wiki" -Filter "*.md" -Recurse | Measure-Object).Count
    Write-Host "Wiki articles: $ArticleCount"
} catch {
    Write-Error "Sync failed: $_"
    exit 1
}
