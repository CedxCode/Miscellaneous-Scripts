# Install-TimeSync.ps1
# Run once as Administrator

$ErrorActionPreference = 'Stop'

$TaskName  = 'Force Time Sync at Startup'
$ScriptDir = Join-Path $env:ProgramData 'TimeSync'
$ScriptPath = Join-Path $ScriptDir 'Sync-Time.ps1'

New-Item -ItemType Directory -Path $ScriptDir -Force | Out-Null

@'
Start-Sleep -Seconds 20

# Make sure the Windows Time service is available
Set-Service w32time -StartupType Automatic
Start-Service w32time -ErrorAction SilentlyContinue

# Use reliable NTP peers
w32tm /config /manualpeerlist:"time.windows.com,0x8 pool.ntp.org,0x8 time.google.com,0x8" /syncfromflags:manual /update | Out-Null

# Try a few times in case networking is not ready yet
for ($i = 1; $i -le 5; $i++) {
    try {
        Restart-Service w32time -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 3
        w32tm /resync /force | Out-Null
        Start-Sleep -Seconds 5
        break
    } catch {
        Start-Sleep -Seconds 5
    }
}
'@ | Set-Content -Path $ScriptPath -Encoding UTF8

$Action    = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""
$Trigger   = New-ScheduledTaskTrigger -AtStartup
$Principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Force | Out-Null

# Run once immediately after installing
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptPath

Write-Host "Installed startup time sync task: $TaskName"
Write-Host "Script saved to: $ScriptPath"
