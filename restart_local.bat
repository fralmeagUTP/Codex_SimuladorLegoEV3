@echo off
setlocal
call "%~dp0scripts\restart_web.cmd" %*
exit /b %ERRORLEVEL%
