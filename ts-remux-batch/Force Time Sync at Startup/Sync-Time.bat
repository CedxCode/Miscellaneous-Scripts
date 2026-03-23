@echo off
echo Synchronizing Windows time...
net start w32time >nul 2>&1
w32tm /resync /force
exit /b
