# setup_scheduled_tasks.ps1 — Register the 3 daily H&E News Clipping runs in
# Windows Task Scheduler. Run this PowerShell script ONCE to install the tasks.
#
# Usage (from PowerShell, in this folder):
#   .\setup_scheduled_tasks.ps1
#
# If PowerShell blocks the script with an execution-policy error, run this first
# in the same PowerShell window:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#
# To REMOVE the tasks later:
#   Unregister-ScheduledTask -TaskName "H&E News Clipping 06-00 BRT" -Confirm:$false
#   Unregister-ScheduledTask -TaskName "H&E News Clipping 16-30 BRT" -Confirm:$false
#   Unregister-ScheduledTask -TaskName "H&E News Clipping 18-00 BRT" -Confirm:$false

# ── Configuration ────────────────────────────────────────────────────────────
$HEFolder = $PSScriptRoot              # the H&E folder this script lives in
$LogFolder = Join-Path $HEFolder "logs"
$ScriptPath = Join-Path $HEFolder "run_daily.py"

# Locate python.exe — and RESOLVE any Windows Store stubs to the real binary.
# The stub at WindowsApps\python.exe goes through a redirect layer that Task
# Scheduler under cmd.exe sometimes can't follow. Asking Python itself for
# sys.executable gives us the underlying real path.
function Find-Python {
    # First try where.exe to find any callable python
    $whereOut = & where.exe python 2>$null | Select-Object -First 1
    $candidate = $null
    if ($whereOut) {
        $candidate = $whereOut
    } else {
        # Fallback common install paths
        $paths = @(
            "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
            "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
            "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
            "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
            "C:\Python313\python.exe", "C:\Python312\python.exe",
            "C:\Python311\python.exe", "C:\Python310\python.exe"
        )
        foreach ($c in $paths) { if (Test-Path $c) { $candidate = $c; break } }
    }
    if (-not $candidate) {
        throw "Could not locate python.exe. Edit `$PythonExe in this script manually."
    }
    # Resolve to real path via sys.executable (bypasses WindowsApps stub)
    try {
        $real = & $candidate -c "import sys; print(sys.executable)" 2>$null
        if ($real -and (Test-Path $real)) {
            return $real
        }
    } catch {}
    # Fall back to the candidate if resolution fails
    return $candidate
}

$PythonExe = Find-Python
Write-Host "Using Python: $PythonExe"
Write-Host "H&E folder:  $HEFolder"
Write-Host "Pipeline:    $ScriptPath"

# Verify
if (-not (Test-Path $ScriptPath)) {
    throw "run_daily.py not found in $HEFolder"
}

# Make logs folder
if (-not (Test-Path $LogFolder)) {
    New-Item -ItemType Directory -Path $LogFolder | Out-Null
    Write-Host "Created log folder: $LogFolder"
}

# ── Task definitions ─────────────────────────────────────────────────────────
# Naming pattern mirrors Rafael's existing TMT tasks ("TMT News Clipping XX-XX BRT")
# so all 6 tasks sit side-by-side in Task Scheduler GUI sorted alphabetically.
$Tasks = @(
    @{ Name = "H&E News Clipping 06-00 BRT";   Time = "06:00"; Desc = "Morning H&E clipping (catches overnight news)" }
    @{ Name = "H&E News Clipping 16-30 BRT";   Time = "16:30"; Desc = "Afternoon H&E clipping (catches midday + post-lunch)" }
    @{ Name = "H&E News Clipping 18-00 BRT";   Time = "18:00"; Desc = "Evening H&E clipping (catches late-afternoon updates)" }
)

# Task settings shared by all three:
#   - Run whether user is logged on or not (highest privileges not required)
#   - Wake the computer to run the task (so 06h fires even if asleep)
#   - Stop the task if it runs longer than 30 minutes (safety)
#   - Retry if missed within next hour (e.g. machine was off)
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -WakeToRun `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
    -RestartCount 1 `
    -RestartInterval (New-TimeSpan -Minutes 15)

$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

foreach ($t in $Tasks) {
    $logFile  = Join-Path $LogFolder "$($t.Name).log"
    # Argument list — change directory then run python with output captured to log
    $cmdLine  = "/c cd /d `"$HEFolder`" && `"$PythonExe`" `"$ScriptPath`" >> `"$logFile`" 2>&1"
    $Action   = New-ScheduledTaskAction -Execute "cmd.exe" -Argument $cmdLine -WorkingDirectory $HEFolder
    $Trigger  = New-ScheduledTaskTrigger -Daily -At $t.Time

    # Remove any existing task with this name (idempotent re-install)
    if (Get-ScheduledTask -TaskName $t.Name -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $t.Name -Confirm:$false
        Write-Host "Removed existing task: $($t.Name)"
    }

    Register-ScheduledTask `
        -TaskName    $t.Name `
        -Action      $Action `
        -Trigger     $Trigger `
        -Settings    $Settings `
        -Principal   $Principal `
        -Description $t.Desc | Out-Null

    Write-Host "[OK] Registered: $($t.Name)   triggers daily at $($t.Time)"
}

Write-Host ""
Write-Host "Done. 3 daily tasks installed."
Write-Host "Logs will be written to: $LogFolder"
Write-Host ""
Write-Host "To verify, run:    Get-ScheduledTask -TaskName 'H&E News Clipping*'"
Write-Host "To run NOW one time (test), run:"
Write-Host "    Start-ScheduledTask -TaskName 'H&E News Clipping 06-00 BRT'"
Write-Host "    Get-Content -Wait '$LogFolder\H&E News Clipping 06-00 BRT.log'   # tail the log"
