@echo off
setlocal enabledelayedexpansion
title Prompt Agent
cd /d "%~dp0"

rem --------------------------------------------------------------
rem  One-click start: web UI (run.py) + feishu channel (feishu_bot.py)
rem  Usage:
rem    start.bat          -> start whatever is not running yet
rem    start.bat restart  -> kill both first, then start fresh
rem  NOTE: keep this file ASCII-only. Chinese output breaks cmd parsing
rem        (UTF-8+chcp truncates lines mid-word; GBK shows mojibake in editors).
rem --------------------------------------------------------------

set "MODE=%~1"
if /i "!MODE!"=="restart" call :kill_all

echo ==================================================
echo    Prompt Agent  -  one-click start (web + feishu)
echo ==================================================
echo.

rem ========== 1. find a Python that has fastapi ==========
set "PY=C:\Python314\python.exe"
if not exist "!PY!" (
  for %%V in (314 313 312 311) do (
    if not exist "!PY!" if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
  )
)
if not exist "!PY!" set "PY=python"

"!PY!" -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
  echo [x] fastapi not found in this Python:
  echo     !PY!
  echo.
  echo     Install deps first, then double-click again:
  echo.
  echo     "!PY!" -m pip install fastapi uvicorn lark-oapi
  echo.
  pause
  exit /b 1
)

rem ========== 2. web service: reuse if already running ==========
set "FOUND="
for /l %%N in (8099,1,8109) do (
  if not defined FOUND (
    set "CODE="
    for /f %%C in ('curl -s -o NUL -w "%%{http_code}" --max-time 1 http://127.0.0.1:%%N/api/skills 2^>NUL') do set "CODE=%%C"
    if "!CODE!"=="200" set "FOUND=%%N"
  )
)
if defined FOUND (
  echo [web] already running on port !FOUND! - opening the page.
  start "" "http://127.0.0.1:!FOUND!"
) else (
  echo [web] not running, will start it now.
)

rem ========== 3. feishu channel: reuse if already running ==========
rem the [t] trick: without it this very powershell command line would
rem match its own filter and always report "already running"
powershell -NoProfile -Command "if (Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*feishu_bo[t].py*' }) { exit 0 } else { exit 1 }"
if not errorlevel 1 (
  echo [feishu] channel already running - skipped.
) else (
  echo [feishu] starting in a separate window ...
  start "Feishu channel (closing this window = channel stopped)" "!PY!" feishu_bot.py
)

rem ========== 4. wrap up ==========
echo.
if defined FOUND (
  echo All set. You can close this window now.
  echo (the feishu channel lives in its own window, unaffected)
  ping -n 3 127.0.0.1 >nul
  exit /b 0
)

echo   Keep this window OPEN - closing it stops the web service.
echo   (the feishu channel runs in its own window, independent)
echo.
echo Starting ... browser will open automatically.
echo.
echo --------------------------------------------------
"!PY!" run.py --port auto --open
echo --------------------------------------------------
echo.
echo Web service stopped. (the feishu channel window is still alive)
pause

rem ========== subroutine: kill both processes ==========
:kill_all
echo [restart] stopping feishu channel ...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*feishu_bo[t].py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
echo [restart] stopping web service (ports 8099-8109) ...
powershell -NoProfile -Command "Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -ge 8099 -and $_.LocalPort -le 8109 -and $_.OwningProcess -ne 0 } | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }"
ping -n 3 127.0.0.1 >nul
goto :eof
