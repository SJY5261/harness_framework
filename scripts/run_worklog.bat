@echo off
chcp 65001 > nul
set "PYTHONUTF8=1"
set "PY=D:\Tool\Python\Python314\python.exe"
for %%I in ("%~dp0..") do set "HARNESS_ROOT=%%~fI"
set "SCRIPT=%HARNESS_ROOT%\scripts\daily_worklog.py"
set "LOG=%HARNESS_ROOT%\logs\worklog_cron.log"

echo ===== %DATE% %TIME% DailyWorklog start =====>> "%LOG%"
if exist "%PY%" goto python_ready
echo [worklog] Python runtime not found: %PY%>> "%LOG%"
echo ===== %DATE% %TIME% DailyWorklog end (exit 3) =====>> "%LOG%"
exit /b 3

:python_ready
"%PY%" "%SCRIPT%" %* >> "%LOG%" 2>&1
set "WORKLOG_RC=%ERRORLEVEL%"
echo ===== %DATE% %TIME% DailyWorklog end (exit %WORKLOG_RC%) =====>> "%LOG%"
exit /b %WORKLOG_RC%
