@echo off
setlocal
call "%~dp0scripts\stop_web.cmd" %*
exit /b %ERRORLEVEL%
