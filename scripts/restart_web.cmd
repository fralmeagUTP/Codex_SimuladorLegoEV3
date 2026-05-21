@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0restart_web.ps1" %*
exit /b %ERRORLEVEL%
