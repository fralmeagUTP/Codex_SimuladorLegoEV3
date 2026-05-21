@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_web_waitress.ps1" %*
exit /b %ERRORLEVEL%
