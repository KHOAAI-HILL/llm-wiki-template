# ============================================================
#  sync-brain.ps1 - Bidirectional sync Second Brain to GitHub
#  Trigger: Called after /brain-compile or /wrapup
#  Repo:    https://github.com/KHOAAI-HILL/lekhoa-second-brain
# ============================================================

# ===== CONFIG =====
$VaultPath   = $PSScriptRoot
$LogFile     = Join-Path $VaultPath "sync-log.txt"
$MaxLogLines = 500
$Branch      = "main"

# ===== LOG =====
function Write-SyncLog {
    param([string]$Status, [string]$Detail)
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $entry = "[$ts] $Status | $Detail"
    Add-Content -Path $LogFile -Value $entry -Encoding UTF8

    if (Test-Path $LogFile) {
        $lines = @(Get-Content $LogFile -Encoding UTF8 -ErrorAction SilentlyContinue)
        if ($lines.Count -gt $MaxLogLines) {
            $lines[($lines.Count - $MaxLogLines)..($lines.Count - 1)] | Set-Content $LogFile -Encoding UTF8
        }
    }
}

# ===== TOAST NOTIFICATION =====
function Send-Toast {
    param([string]$Title, [string]$Message)

    try {
        [void][Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]
        [void][Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime]

        $toastXml = @"
<toast>
  <visual>
    <binding template="ToastGeneric">
      <text>$Title</text>
      <text>$Message</text>
    </binding>
  </visual>
</toast>
"@
        $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        $xml.LoadXml($toastXml)
        $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("SecondBrain.Sync")
        $notifier.Show($toast)
    }
    catch {
        Write-SyncLog "TOAST_FAIL" "Toast error: $($_.Exception.Message)"
    }
}

# ===== GUARD: Wait for OneDrive to finish syncing =====
function Wait-OneDriveIdle {
    $maxWait = 60
    $waited  = 0
    while ($waited -lt $maxWait) {
        $tmpFiles = @(Get-ChildItem -Path $VaultPath -Recurse -ErrorAction SilentlyContinue |
                      Where-Object { $_.Name -like '~$*' -and $_.Extension -eq '.tmp' })
        if ($tmpFiles.Count -eq 0) {
            return $true
        }
        Write-SyncLog "WAIT" "OneDrive syncing... ($waited/$maxWait s)"
        Start-Sleep -Seconds 5
        $waited += 5
    }
    return $false
}

# ===== MAIN SYNC =====
function Invoke-BrainSync {
    Set-Location $VaultPath

    # 1. Guard: OneDrive
    if (-not (Wait-OneDriveIdle)) {
        Write-SyncLog "SKIP" "OneDrive still syncing after 60s timeout"
        Send-Toast "Brain Sync - Skipped" "OneDrive is busy. Try again later."
        return 1
    }

    # 2. Network check
    $canReach = Test-Connection -ComputerName "github.com" -Count 1 -Quiet -ErrorAction SilentlyContinue
    if (-not $canReach) {
        Write-SyncLog "SKIP" "No network to github.com"
        Send-Toast "Brain Sync - Offline" "Cannot reach GitHub. Sync skipped."
        return 1
    }

    # 3. Fetch remote
    $fetchOut = git fetch origin 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        Write-SyncLog "ERROR" "git fetch failed: $fetchOut"
        Send-Toast "Brain Sync - Error" "git fetch failed."
        return 1
    }

    # 4. Pull if remote has changes (from Hermes/Railway)
    $localHead  = (git rev-parse HEAD 2>&1 | Out-String).Trim()
    $remoteHead = (git rev-parse "origin/$Branch" 2>&1 | Out-String).Trim()

    $pulled = $false
    if ($localHead -ne $remoteHead) {
        $behindStr = (git rev-list --count "HEAD..origin/$Branch" 2>&1 | Out-String).Trim()
        $behindCount = 0
        if ([int]::TryParse($behindStr, [ref]$behindCount) -and $behindCount -gt 0) {
            Write-SyncLog "PULL" "Remote ahead $behindCount commit(s) - pulling..."

            # Stash local changes before pull
            $hasChanges = (git status --porcelain 2>&1 | Out-String).Trim()
            $stashed = $false
            if ($hasChanges) {
                git stash push -m "auto-stash-before-sync" 2>&1 | Out-Null
                $stashed = $true
            }

            $pullOut = git pull --rebase origin $Branch 2>&1 | Out-String
            if ($LASTEXITCODE -ne 0) {
                git rebase --abort 2>&1 | Out-Null
                if ($stashed) {
                    git stash pop 2>&1 | Out-Null
                }
                Write-SyncLog "CONFLICT" "Rebase conflict - aborted. Manual resolve needed."
                Send-Toast "Brain Sync - Conflict!" "Git conflict when pulling from Hermes. Manual resolve needed."
                return 1
            }

            if ($stashed) {
                $popOut = git stash pop 2>&1 | Out-String
                if ($LASTEXITCODE -ne 0) {
                    Write-SyncLog "CONFLICT" "Stash pop conflict: $popOut"
                    Send-Toast "Brain Sync - Stash Conflict" "Local changes conflict with remote. Manual resolve needed."
                    return 1
                }
            }

            $pulled = $true
            Write-SyncLog "PULL" "Pulled $behindCount commit(s) from remote OK"
        }
    }

    # 4.5 Rebuild Graph and Index
    Write-SyncLog "BUILD" "Rebuilding knowledge graph and search index..."
    python wiki/_build_graph.py 2>&1 | Out-Null
    python scripts/brain.py index 2>&1 | Out-Null
    Write-SyncLog "BUILD" "Graph/Index updated"

    # 5. Commit local changes
    $statusOutput = @(git status --porcelain 2>&1)
    $pushed = $false

    if ($statusOutput.Count -gt 0 -and $statusOutput[0]) {
        $statusLines = $statusOutput | Where-Object { $_ -ne "" }
        $addedCount    = @($statusLines | Where-Object { $_ -match '^\?\?' }).Count
        $modifiedCount = @($statusLines | Where-Object { $_ -match '^\s?M' }).Count
        $deletedCount  = @($statusLines | Where-Object { $_ -match '^\s?D' }).Count
        $summary = "+$addedCount ~$modifiedCount -$deletedCount"

        git add . 2>&1 | Out-Null
        $commitTs = Get-Date -Format "yyyy-MM-ddTHH:mm"
        git commit -m "auto-sync: $commitTs | $summary" 2>&1 | Out-Null

        if ($LASTEXITCODE -ne 0) {
            Write-SyncLog "ERROR" "git commit failed"
            Send-Toast "Brain Sync - Error" "git commit failed."
            return 1
        }

        Write-SyncLog "COMMIT" "Committed local changes: $summary"
        $pushed = $true
    }

    # 6. Push if needed
    if ($pushed -or $pulled) {
        $aheadStr = (git rev-list --count "origin/$Branch..HEAD" 2>&1 | Out-String).Trim()
        $aheadCount = 0
        if ([int]::TryParse($aheadStr, [ref]$aheadCount) -and $aheadCount -gt 0) {
            $pushOut = git push origin $Branch 2>&1 | Out-String
            if ($LASTEXITCODE -ne 0) {
                Write-SyncLog "ERROR" "git push failed: $pushOut"
                Send-Toast "Brain Sync - Push Error" "Cannot push to GitHub."
                return 1
            }
            Write-SyncLog "PUSH" "Pushed $aheadCount commit(s) to remote"
        }
    }
    else {
        Write-SyncLog "OK" "Already in sync - no changes"
    }

    return 0
}

# ===== RUN =====
Write-SyncLog "START" "=== Sync triggered ==="
$exitCode = Invoke-BrainSync

if ($exitCode -eq 0) {
    Write-SyncLog "DONE" "Sync completed successfully"
    $lastLines = Get-Content $LogFile -Tail 5 -Encoding UTF8 -ErrorAction SilentlyContinue
    if ($lastLines -match "PUSH|PULL|COMMIT") {
        Send-Toast "Brain Sync - OK" "Sync completed successfully!"
    }
}

exit $exitCode
