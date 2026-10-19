@echo off
setlocal enabledelayedexpansion
title Prompt Agent
cd /d "%~dp0"
set "PBASE=%~dp0"

rem --------------------------------------------------------------
rem  Prompt Agent - one-click start
rem
rem  Usage:
rem    start.bat            -> start both in the BACKGROUND, no window at all
rem    start.bat fg         -> start in THIS window with live logs (debugging)
rem    start.bat stop       -> stop both
rem    start.bat restart    -> stop, then start in the background
rem    start.bat check      -> only report which Python / deps it found
rem    start.bat open       -> just open the page of the running service
rem    start.bat lan        -> serve to the LOCAL NETWORK on 8099 (colleagues can browse)
rem    start.bat lan write  -> same, but let guests generate / change settings too
rem
rem  lan mode binds 0.0.0.0 instead of 127.0.0.1. Guests are READ-ONLY by default
rem  (browse cases only) - this box keeps full rights. Everything is unauthenticated,
rem  so never use lan mode on a network you do not trust.
rem
rem  Background mode launches pythonw.exe (no console) through
rem  scripts\_silent.pyw, which redirects stdout/stderr to
rem      logs\run.log        and  logs\feishu_bot.log
rem  Those two files are the ONLY way to see output in background mode.
rem
rem  Python discovery order (first hit wins):
rem    1. .venv\Scripts\python.exe   (project venv - this is where deps go)
rem    2. C:\Python3xx\python.exe    (python.org installer, default path)
rem    3. %LOCALAPPDATA%\Programs\Python\Python3xx\python.exe
rem    4. py -3 launcher
rem    5. python on PATH
rem  If none has the deps, it creates .venv with the first Python it found and
rem  installs requirements.txt into it. Nothing is installed system-wide.
rem
rem  NOTE: keep this file ASCII-only. Chinese output breaks cmd parsing
rem        (UTF-8+chcp truncates lines mid-word; GBK shows mojibake in editors).
rem --------------------------------------------------------------

set "MODE=%~1"
if not defined MODE set "MODE=silent"
if /i "!MODE!"=="bg" set "MODE=silent"

if /i "!MODE!"=="stop" goto :do_stop
if /i "!MODE!"=="restart" call :kill_all

echo ==================================================
echo    Prompt Agent  -  one-click start (web + feishu)
echo ==================================================
echo.

rem ========== 1. locate a Python ==========
set "PY="
set "VENV=%~dp0.venv\Scripts\python.exe"

rem (a) project venv wins - that is the one we install deps into
if exist "!VENV!" set "PY=!VENV!"

rem (b) common install locations
if not defined PY (
  for %%P in (
    "C:\Python314\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
  ) do if not defined PY if exist "%%~P" set "PY=%%~P"
)

rem (c) py launcher (shipped by the python.org installer)
if not defined PY (
  for /f "delims=" %%E in ('py -3 -c "import sys;print(sys.executable)" 2^>nul') do (
    if not defined PY set "PY=%%E"
  )
)

rem (d) plain python on PATH
if not defined PY (
  for /f "delims=" %%E in ('python -c "import sys;print(sys.executable)" 2^>nul') do (
    if not defined PY set "PY=%%E"
  )
)

if not defined PY goto :no_python
echo [py] !PY!

rem pythonw.exe sits next to python.exe in every normal install, and in .venv too.
rem needed by both background mode and [check], so it must be resolved BEFORE the
rem check-mode jump below - otherwise [check] always reports it as MISSING.
set "PYW=!PY:python.exe=pythonw.exe!"
if not exist "!PYW!" set "PYW=!PY!"

rem check mode is read-only: report what is there, change nothing.
if /i "!MODE!"=="check" goto :do_check

rem ========== 2. make sure dependencies are present ==========
rem openai is a hard import in app/agent.py - without it the server dies on boot,
rem so it belongs in this probe and not only in [check].
"!PY!" -c "import importlib.util as u, sys; sys.exit(0 if all(u.find_spec(m) for m in ('fastapi','uvicorn','openai')) else 1)" >nul 2>&1
if not errorlevel 1 goto :deps_ok

if exist "!VENV!" (
  echo [py] deps missing in .venv - installing requirements ...
  "!PY!" -m pip install -r requirements.txt
) else (
  echo [py] deps missing - creating .venv and installing requirements ...
  echo      ^(first run only, takes a minute^)
  "!PY!" -m venv ".venv"
  if errorlevel 1 goto :venv_fail
  set "PY=!VENV!"
  "!PY!" -m pip install --upgrade pip >nul 2>&1
  "!PY!" -m pip install -r requirements.txt
)
"!PY!" -c "import importlib.util as u, sys; sys.exit(0 if all(u.find_spec(m) for m in ('fastapi','uvicorn','openai')) else 1)" >nul 2>&1
if errorlevel 1 goto :no_deps
echo [py] deps ready.
:deps_ok

if /i "!MODE!"=="open" goto :do_open
if /i "!MODE!"=="lan" goto :run_lan

rem ========== 3. is the web service already up? ==========
call :probe_web
if defined FOUND goto :already_up

if /i "!MODE!"=="fg" goto :run_fg

rem ---------- 4. background start (default) ----------
rem pythonw = no console window. _silent.pyw takes over stdout/stderr so the
rem scripts can still print, and writes their pid for `start.bat stop`.
rem It is a real file, not a test helper: without it nothing starts at all.
if not exist "scripts\_silent.pyw" goto :no_launcher
if not exist "logs" mkdir "logs" >nul 2>&1

rem feishu first: `start` returns immediately, so its pid file is written while
rem we are still waiting for the web service - no extra waiting afterwards.
rem find_spec only looks the module up, it does NOT import it: a real
rem "import lark_oapi" costs ~10s on this machine and made the window hang.
"!PY!" -c "import importlib.util as u, sys; sys.exit(0 if u.find_spec('lark_oapi') else 1)" >nul 2>&1
if errorlevel 1 goto :feishu_skip

rem do NOT start a second channel. Two long connections on the same app split
rem the incoming events between them, i.e. replies land on the wrong process or
rem get lost. Happens when the web service died but the channel survived.
call :probe_feishu
if defined FOK goto :feishu_already
echo [feishu] starting in background ...
rem truncate only here: the file is locked while a channel is running, and
rem "type nul >" against a locked file prints a scary error we cannot redirect.
type nul > "logs\feishu_bot.log" 2>nul
start "" "!PYW!" "scripts\_silent.pyw" feishu_bot.py
set "LARK_OK=1"
goto :feishu_done

:feishu_already
echo [feishu] already running, pid !FOK! - not starting a second one.
set "LARK_OK=1"
goto :feishu_done

:feishu_skip
echo [feishu] lark-oapi not installed - channel skipped.
echo          fix: "!PY!" -m pip install lark-oapi
:feishu_done

echo [web] starting in background ...
rem safe to truncate here: we only get this far when nothing is listening on
rem 8099-8109, so no old run.log is holding the file open
type nul > "logs\run.log" 2>nul
start "" "!PYW!" "scripts\_silent.pyw" run.py --port auto --open

rem cold start measured at ~3s here; allow up to ~20s on a slow disk
set /a TRIES=0
:wait_web
call :probe_web
if defined FOUND goto :started
set /a TRIES+=1
if !TRIES! GEQ 20 goto :start_failed
ping -n 2 127.0.0.1 >nul
goto :wait_web

:started
rem the pid file lands ~1s after the launch above
if not defined LARK_OK goto :print_summary
set /a FTRIES=0
:wait_feishu
call :probe_feishu
if defined FOK goto :print_summary
set /a FTRIES+=1
if !FTRIES! GEQ 4 goto :print_summary
ping -n 2 127.0.0.1 >nul
goto :wait_feishu

:print_summary
echo.
echo [ok] web    : http://127.0.0.1:!FOUND!   (browser opened)
if not defined LARK_OK (
  echo [--] feishu : skipped, lark-oapi missing
) else (
  if defined FOK (
    echo [ok] feishu : running, pid !FOK!
  ) else (
    echo [warn] feishu : process not found - see logs\feishu_bot.log
  )
)
echo [ok] logs   : logs\run.log  and  logs\feishu_bot.log
echo [ok] stop   : double-click start.bat with argument  stop
echo.
echo No window stays open. This one closes itself now.
ping -n 2 127.0.0.1 >nul
exit /b 0

:start_failed
rem two very different situations look the same from the outside:
rem   process gone  -> it crashed, the log tail is what matters
rem   process alive -> just slow (cold cache), it will open on its own
call :probe_wproc
if defined WOK goto :still_starting
echo.
echo [x] The web service died on startup.
echo     Last lines of logs\run.log:
echo --------------------------------------------------
if exist "logs\run.log" (type "logs\run.log") else (echo ^(no log file^))
echo --------------------------------------------------
echo.
pause
exit /b 1

:still_starting
echo.
echo [..] The web process is alive (pid !WOK!) but not answering yet.
echo      Cold start is usually ~3s; a cold disk cache can make it longer.
echo      The browser will open by itself when it is ready.
echo      If nothing happens after a minute, run:  start.bat check
echo.
ping -n 3 127.0.0.1 >nul
exit /b 0

rem ========== mode: already running ==========
:already_up
echo [web] already running on port !FOUND! - opening the page.
start "" "http://127.0.0.1:!FOUND!"
echo.
echo Nothing started, nothing stopped. Closing in 2s.
ping -n 3 127.0.0.1 >nul
exit /b 0

rem ========== mode: open the page only ==========
:do_open
call :probe_web
if defined FOUND (
  echo [web] running on port !FOUND! - opening.
  start "" "http://127.0.0.1:!FOUND!"
  ping -n 3 127.0.0.1 >nul
) else (
  echo [web] not running. Run start.bat first.
  echo.
  pause
)
exit /b 0

rem ========== mode: local network (colleagues can browse) ==========
rem 0.0.0.0 = listen on every adapter, so other PCs can reach this one.
rem Fixed port 8099 on purpose: colleagues get a URL they can bookmark, and it
rem is the same port the normal mode uses, so the two never fight for it.
:run_lan
if not exist "scripts\_silent.pyw" goto :no_launcher
if not exist "scripts\lan_ip.py" goto :no_launcher
if not exist "logs" mkdir "logs" >nul 2>&1
set "LANWRITE="
if /i "%~2"=="write" set "LANWRITE=--allow-guest-write"

call :probe_web
if defined FOUND (
  call :get_lanip
  echo [lan] already running on port !FOUND! - nothing to do.
  if defined LANIP echo [lan] colleagues open:  http://!LANIP!:!FOUND!
  echo.
  pause
  exit /b 0
)

echo [lan] starting on 0.0.0.0:8099 ...
if defined LANWRITE (echo [lan] guests MAY generate and change settings.) else (echo [lan] guests are READ-ONLY (browse only^).)
type nul > "logs\run.log" 2>nul
start "" "!PYW!" "scripts\_silent.pyw" run.py --host 0.0.0.0 --port 8099 --open !LANWRITE!

set /a TRIES=0
:lan_wait
call :probe_web
if defined FOUND goto :lan_up
set /a TRIES+=1
if !TRIES! GEQ 20 goto :start_failed
ping -n 2 127.0.0.1 >nul
goto :lan_wait

:lan_up
call :get_lanip
echo.
echo ==================================================
echo   This PC   : http://127.0.0.1:!FOUND!
if defined LANIP (
  echo   Colleagues: http://!LANIP!:!FOUND!
) else (
  echo   Colleagues: could not detect the LAN ip -
  echo               run "ipconfig" and look for the IPv4 address
)
echo ==================================================
echo.
if defined LANWRITE (
  echo [i] Guests can generate and change settings. Your API quota is shared.
) else (
  echo [i] Guests can only BROWSE. Clicking generate from another PC returns 403.
  echo     Want them to generate too?  start.bat lan write
)
echo.
echo [i] If another PC cannot connect, Windows Firewall is blocking it.
echo     Allow it once in an admin cmd:
echo       netsh advfirewall firewall add rule name="PromptAgent 8099" dir=in action=allow protocol=TCP localport=8099
echo.
echo Keep this window open for the address above, or press any key to close
echo (the service keeps running in the background either way).
pause
exit /b 0

rem ========== mode: foreground (live logs in this window) ==========
:run_fg
echo [web] starting in THIS window - keep it open, closing it stops the web.
echo [feishu] starting in its own window.
echo.

powershell -NoProfile -Command "if (Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^pythonw?\.exe$' -and $_.CommandLine -like '*feishu_bo[t].py*' }) { exit 0 } else { exit 1 }"
if not errorlevel 1 (
  echo [feishu] channel already running - skipped.
) else (
  start "Feishu channel (closing this window = channel stopped)" "!PY!" feishu_bot.py
)

echo.
echo --------------------------------------------------
"!PY!" run.py --port auto --open
echo --------------------------------------------------
echo.
echo Web service stopped. (the feishu channel window is still alive)
pause

rem without this the flow fell through into :kill_all below
goto :eof

rem ========== mode: check only ==========
:do_check
echo.
echo [check] python    : !PY!
"!PY!" -c "import fastapi" >nul 2>&1
if errorlevel 1 (echo [check] fastapi   : MISSING) else (echo [check] fastapi   : ok)
"!PY!" -c "import uvicorn" >nul 2>&1
if errorlevel 1 (echo [check] uvicorn   : MISSING) else (echo [check] uvicorn   : ok)
"!PY!" -c "import openai" >nul 2>&1
if errorlevel 1 (echo [check] openai    : MISSING) else (echo [check] openai    : ok)
"!PY!" -c "import yaml" >nul 2>&1
if errorlevel 1 (echo [check] pyyaml    : MISSING) else (echo [check] pyyaml    : ok)
"!PY!" -c "import lark_oapi" >nul 2>&1
if errorlevel 1 (echo [check] lark-oapi  : MISSING - feishu channel will fail) else (echo [check] lark-oapi  : ok)
if exist "!PYW!" (echo [check] pythonw   : ok) else (echo [check] pythonw   : MISSING - background mode falls back to a visible window)
if exist "scripts\_silent.pyw" (echo [check] launcher  : ok) else (echo [check] launcher  : MISSING - background mode cannot start anything)
if exist "scripts\lan_ip.py" (echo [check] lan ip    : ok) else (echo [check] lan ip    : MISSING - "start.bat lan" cannot show your address)
if exist config.json (echo [check] config    : config.json found) else (echo [check] config    : MISSING - copy config.example.json first)
if exist skills\seedance-prompt-library (echo [check] skills    : found) else (echo [check] skills    : MISSING)
echo.
call :probe_web
if defined FOUND (echo [check] running   : web up, port !FOUND!) else (echo [check] running   : web is NOT running)
call :probe_feishu
if defined FOK (echo [check]           : feishu up, pid !FOK!) else (echo [check]           : feishu is NOT running)
echo.
pause
exit /b 0

rem ========== mode: stop ==========
:do_stop
call :kill_all
echo [stop] done.
ping -n 3 127.0.0.1 >nul
exit /b 0

rem ========== error paths ==========
:no_launcher
echo [x] A launcher script is missing.
echo.
echo     Background mode needs scripts\_silent.pyw: pythonw has no console, so
echo     sys.stdout is None and any print() would kill the script. It redirects
echo     the output to logs\ and records the pid that `start.bat stop` uses.
echo     lan mode additionally needs scripts\lan_ip.py (works out this PC's ip).
echo.
echo     Restore from git:
echo       git checkout -- scripts/_silent.pyw scripts/lan_ip.py
echo.
echo     Or just run the old way, with a visible window:
echo       start.bat fg
echo.
pause
exit /b 1

:no_python
echo [x] No Python found on this machine.
echo.
echo     Install Python 3.11 or newer and tick "Add python.exe to PATH":
echo       https://www.python.org/downloads/windows/
echo.
echo     Then double-click start.bat again - it will build .venv by itself.
echo.
pause
exit /b 1

:venv_fail
echo [x] Could not create .venv with:
echo       !PY!
echo     Try by hand:
echo       "!PY!" -m venv .venv
echo.
pause
exit /b 1

:no_deps
echo [x] Dependency install failed. Run this by hand and read the error:
echo.
echo       "!PY!" -m pip install -r requirements.txt
echo.
pause
exit /b 1

rem ========== helper: this PC's LAN ip (empty if not on a network) ==========
rem ipconfig parsing was rejected: the label is localised ("IPv4 地址" on zh-CN)
rem and virtual adapters often come first. scripts\lan_ip.py asks the OS which
rem adapter the default route uses, which is the one colleagues can reach.
:get_lanip
set "LANIP="
if not exist "logs" mkdir "logs" >nul 2>&1
rem NOT for /f: when the command starts with a quoted path, cmd eats the outer
rem quotes and the whole thing fails silently. Redirect to a file, read it back.
"!PY!" "scripts\lan_ip.py" > "logs\_lanip.txt" 2>nul
if exist "logs\_lanip.txt" (
  set /p LANIP=<"logs\_lanip.txt"
  del /q "logs\_lanip.txt" >nul 2>&1
)
goto :eof

rem ========== helper: probe ports 8099-8109 for a live /api/skills ==========
rem Do NOT brute-force the range with curl. On this machine a curl against a
rem closed port does not get "connection refused", it sits there until --max-time
rem (measured 1.2s each), so 12 ports cost 13.5s - and this helper runs once per
rem retry in the wait loop, which is where the window used to sit for 35s.
rem netstat answers in ~150ms and tells us exactly which ports are listening;
rem we then curl only those, which returns instantly because they are alive.
:probe_web
set "FOUND="
set "CANDS="
for /f "tokens=3 delims=: " %%P in ('netstat -an ^| findstr /i "LISTENING"') do (
  if %%P GEQ 8099 if %%P LEQ 8109 set "CANDS=!CANDS! %%P"
)
if not defined CANDS goto :eof
for %%P in (!CANDS!) do (
  set "CODE="
  for /f %%C in ('curl -s --noproxy "*" -o NUL -w "%%{http_code}" --max-time 2 http://127.0.0.1:%%P/api/skills 2^>NUL') do set "CODE=%%C"
  if "!CODE!"=="200" set "FOUND=%%P"
)
goto :eof

rem ========== helper: is the web process alive (even if not listening yet)? ==========
:probe_wproc
set "WOK="
if not exist "logs\run.pid" goto :eof
set "WPID="
set /p WPID=<"logs\run.pid"
if not defined WPID goto :eof
tasklist /FI "PID eq !WPID!" /NH 2>nul | findstr /i "pythonw" >nul
if errorlevel 1 goto :eof
set "WOK=!WPID!"
goto :eof

rem ========== helper: is the feishu channel process alive? ==========
rem the pid file is written by _silent.pyw the moment it starts, so this answers
rem "the process exists", not "the long connection is up". The connection line
rem only appears in logs\feishu_bot.log about 10s later - that import is slow.
:probe_feishu
set "FOK="
if not exist "logs\feishu_bot.pid" goto :eof
set "FPID="
set /p FPID=<"logs\feishu_bot.pid"
if not defined FPID goto :eof
tasklist /FI "PID eq !FPID!" /NH 2>nul | findstr /i "pythonw" >nul
if errorlevel 1 goto :eof
set "FOK=!FPID!"
goto :eof

rem ========== subroutine: stop both processes ==========
:kill_all
echo [stop] stopping ...
rem 1) the pids recorded by scripts\_silent.pyw - exact, no guessing
for %%F in ("logs\run.pid" "logs\feishu_bot.pid") do (
  if exist "%%~F" (
    set "PID="
    set /p PID=<"%%~F"
    if defined PID taskkill /PID !PID! /T /F >nul 2>&1
    del /q "%%~F" >nul 2>&1
  )
)
rem 2) sweep anything left from this folder (covers fg mode and stale pid files).
rem    the [t] / [y] tricks stop this very command line from matching itself.
powershell -NoProfile -Command "$b=$env:PBASE.TrimEnd('\'); Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^pythonw?\.exe$' -and $_.CommandLine -and ($_.CommandLine.Contains($b) -or $_.CommandLine -like '*feishu_bo[t].py*' -or $_.CommandLine -like '*run.p[y]*') } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"
rem 3) let go of the ports before anyone restarts
ping -n 3 127.0.0.1 >nul
goto :eof
