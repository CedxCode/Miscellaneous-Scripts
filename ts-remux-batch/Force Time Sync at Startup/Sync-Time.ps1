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
