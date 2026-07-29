@echo off
chcp 65001 > nul
set "PYTHONUTF8=1"
set "PY=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
for %%I in ("%~dp0..") do set "HARNESS_ROOT=%%~fI"
set "SCRIPT=%HARNESS_ROOT%\scripts\daily_worklog.py"
set "LOG=%HARNESS_ROOT%\logs\worklog_cron.log"

echo ===== %DATE% %TIME% DailyWorklog start =====>> "%LOG%"
"%PY%" "%SCRIPT%" %* >> "%LOG%" 2>&1
echo ===== %DATE% %TIME% DailyWorklog end (exit %ERRORLEVEL%) =====>> "%LOG%"
