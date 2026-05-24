@echo off
setlocal
if "%~1"=="" (
  call "%~dp0scripts\start_web.cmd" -Foreground
) else (
  call "%~dp0scripts\start_web.cmd" %*
)
exit /b %ERRORLEVEL%
