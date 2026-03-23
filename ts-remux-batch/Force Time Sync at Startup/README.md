Force Time Sync at Startup

A small PowerShell-based utility for Windows that automatically refreshes system time during startup. It is useful on machines where the clock drifts after being powered off for a few hours and needs a manual sync after every restart.

What this project does

This script:

creates a startup task that runs with elevated privileges,

waits for the system to finish booting,

starts the Windows Time service,

points Windows to reliable NTP servers,

forces a time resynchronization,

retries a few times in case networking is not ready yet.


Why this is useful

Some Windows PCs lose time when powered off for a while. The common causes are:

a weak CMOS/RTC battery,

an unstable Windows Time service,

slow network initialization during boot,

a bad or unavailable NTP source.


This script helps with the software side of the problem. If the PC clock is drifting by hours, the hardware clock battery may still need attention.


---

Files in this project

Install-TimeSync.ps1

This is the installer script. You run it once as Administrator. It then:

creates a working folder under C:\ProgramData\TimeSync,

writes the actual sync script there,

registers a scheduled task to run it at startup,

runs it immediately once after installation.


Sync-Time.ps1

This is the actual startup script created by the installer. It is the script that runs at boot.


---

How to install

1. Save Install-TimeSync.ps1 somewhere on your PC.


2. Open PowerShell as Administrator.


3. Run:



Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PWD\Install-TimeSync.ps1`""

If the file is in another folder, use the full path:

Start-Process powershell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"C:\Path\To\Install-TimeSync.ps1`""


---

What the installer script does, line by line

Below is the same installer script, followed by a plain-English explanation of each part.

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

Explanation

# Install-TimeSync.ps1

A comment. It does not change behavior. It just identifies the file.

# Run once as Administrator

Another comment. This is important because registering a startup task with elevated privileges requires admin rights.

$ErrorActionPreference = 'Stop'

Tells PowerShell to treat errors as terminating errors. This makes the script fail fast instead of silently continuing after a problem.

$TaskName  = 'Force Time Sync at Startup'

Stores the scheduled task name in a variable so it is easy to reuse later.

$ScriptDir = Join-Path $env:ProgramData 'TimeSync'

Builds a folder path inside C:\ProgramData\TimeSync.

$env:ProgramData points to the shared system data folder.

Join-Path safely combines paths.


$ScriptPath = Join-Path $ScriptDir 'Sync-Time.ps1'

Builds the full path for the generated startup script.

New-Item -ItemType Directory -Path $ScriptDir -Force | Out-Null

Creates the folder if it does not already exist.

-Force avoids errors if the folder already exists.

| Out-Null hides the command output.


@' ... '@ | Set-Content -Path $ScriptPath -Encoding UTF8

This block writes the actual startup script into Sync-Time.ps1.

@' and '@ define a multiline literal string.

Everything inside becomes the content of the script file.

Set-Content saves it to disk.

-Encoding UTF8 ensures the file is stored in a modern text encoding.



---

What the generated startup script does, line by line

Here is the script that gets created in C:\ProgramData\TimeSync\Sync-Time.ps1.

Start-Sleep -Seconds 20

Waits 20 seconds after startup. This gives Windows time to bring up networking and background services before attempting synchronization.

Set-Service w32time -StartupType Automatic

Ensures the Windows Time service is allowed to start automatically.

Start-Service w32time -ErrorAction SilentlyContinue

Starts the Windows Time service if it is not already running.

-ErrorAction SilentlyContinue prevents the script from stopping if the service is already running or cannot be started immediately.


w32tm /config /manualpeerlist:"time.windows.com,0x8 pool.ntp.org,0x8 time.google.com,0x8" /syncfromflags:manual /update | Out-Null

Configures Windows Time to use specific NTP servers.

time.windows.com, pool.ntp.org, and time.google.com are common time sources.

0x8 tells Windows to treat them as manual NTP peers.

/syncfromflags:manual switches synchronization to the manual peer list.

/update applies the changes immediately.

Out-Null hides normal command output.


for ($i = 1; $i -le 5; $i++) {

Starts a retry loop that can run up to 5 times.

try {

Begins a block that may fail and should be retried if needed.

Restart-Service w32time -Force -ErrorAction SilentlyContinue

Restarts the Windows Time service to refresh its state.

Start-Sleep -Seconds 3

Waits a few seconds after restarting the service.

w32tm /resync /force | Out-Null

Forces an immediate time synchronization.

Start-Sleep -Seconds 5

Gives Windows time to complete the sync.

break

Exits the retry loop once synchronization succeeds.

} catch {
        Start-Sleep -Seconds 5
    }

If something fails, the script waits 5 seconds and tries again.

}

Ends the retry loop.


---

Creating the scheduled task

$Action    = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""

Creates the action that the task will run.

powershell.exe is the executable.

-NoProfile keeps user profile settings from interfering.

-ExecutionPolicy Bypass allows the script to run without policy blocking.

-File points to the generated script.


$Trigger   = New-ScheduledTaskTrigger -AtStartup

Makes the task run every time Windows starts.

$Principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest

Runs the task using the built-in SYSTEM account with the highest privileges.

This is useful because startup time synchronization often works better with full privileges than with a normal user session.

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Force | Out-Null

Registers the task with Task Scheduler.

-Force replaces an existing task with the same name.

Out-Null hides the output.


powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptPath

Runs the generated script once immediately after installation so you do not need to wait for the next reboot.

Write-Host "Installed startup time sync task: $TaskName"
Write-Host "Script saved to: $ScriptPath"

Prints a success message so you know where the task and script were created.


---

How to run it manually later

You can run the generated sync script manually at any time:

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\ProgramData\TimeSync\Sync-Time.ps1"

Or from an elevated PowerShell session:

C:\ProgramData\TimeSync\Sync-Time.ps1


---

How to uninstall and remove it

If you no longer need the automatic sync, remove the scheduled task and delete the script files.

Remove the scheduled task

Open PowerShell as Administrator and run:

Unregister-ScheduledTask -TaskName "Force Time Sync at Startup" -Confirm:$false

Delete the files

Remove-Item -Path "C:\ProgramData\TimeSync" -Recurse -Force

That removes the generated script folder and its contents.


---

How to restore default Windows Time behavior

If you want to return Windows Time to a clean default state, use these steps in an elevated PowerShell window.

1) Remove the startup task

Unregister-ScheduledTask -TaskName "Force Time Sync at Startup" -Confirm:$false

2) Re-register the Windows Time service

w32tm /unregister
w32tm /register

This resets the Windows Time service registration.

3) Restore a standard service startup mode

sc.exe config w32time start= demand

This returns the service to a normal on-demand style startup behavior.

4) Restart the service

net stop w32time
net start w32time

5) Remove the custom files

Remove-Item -Path "C:\ProgramData\TimeSync" -Recurse -Force


---

Alternative ways to achieve the same result

Option 1: Task Scheduler only

You can skip the installer script entirely and create a task manually:

Open Task Scheduler

Create a new task

Set it to run at startup

Run it with highest privileges

Point it to a PowerShell command that runs Sync-Time.ps1


This is a good option if you prefer a GUI setup.

Option 2: A simple batch file

A .bat file can do the resync with fewer lines, but it is less flexible and less reliable than PowerShell for retry logic and task creation.

Option 3: Domain-managed time sync

On business networks, Group Policy or domain hierarchy time sync may be a better long-term solution than a local script.

Option 4: Fix the hardware clock

If the machine consistently loses hours when powered off, the RTC/CMOS battery should be checked. No script can fully compensate for a dead hardware clock battery.


---

Notes and limitations

This script assumes the machine has internet access after startup.

It is most useful for standalone PCs or desktops that drift over time.

If the system is domain-joined, company time policy may override manual peers.

If the clock is drifting badly, consider checking the motherboard battery.



---

License

Choose any license you want for the GitHub repository, such as MIT or Apache-2.0.


---

Repository suggestion

A clean repository structure could look like this:

TimeSync/
├─ Install-TimeSync.ps1
├─ Sync-Time.ps1
└─ README.md

If you want, I can turn this into a polished GitHub-ready README.md file with badges, a table of contents, and copy-paste command blocks already formatted for publishing.
