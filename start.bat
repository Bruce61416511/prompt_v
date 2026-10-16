@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title 提示词智能体
cd /d "%~dp0"

echo ==================================================
echo    提示词智能体  ·  一键启动
echo ==================================================
echo.

rem ========== 1. 找一个装了 fastapi 的 Python ==========
set "PY=C:\Python314\python.exe"
if not exist "!PY!" (
  for %%V in (314 313 312 311) do (
    if not exist "!PY!" if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" set "PY=%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
  )
)
if not exist "!PY!" set "PY=python"

"!PY!" -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
  echo [x] 这个 Python 里没装 fastapi：
  echo     !PY!
  echo.
  echo     先执行下面这行把依赖装好，再双击本文件：
  echo.
  echo     "!PY!" -m pip install fastapi uvicorn
  echo.
  pause
  exit /b 1
)

rem ========== 2. 服务已经在跑？直接开页面，不重复启动 ==========
set "FOUND="
for /l %%N in (8099,1,8109) do (
  if not defined FOUND (
    set "CODE="
    for /f %%C in ('curl -s -o NUL -w "%%{http_code}" --max-time 1 http://127.0.0.1:%%N/api/skills 2^>NUL') do set "CODE=%%C"
    if "!CODE!"=="200" set "FOUND=%%N"
  )
)
if defined FOUND (
  echo 服务已经在运行了（端口 !FOUND!），直接打开页面。
  start "" "http://127.0.0.1:!FOUND!"
  ping -n 2 127.0.0.1 >nul
  exit /b 0
)

rem ========== 3. 启动 ==========
echo 正在启动服务，浏览器会自动打开 ...
echo.
echo   注意：这个窗口不要关。关掉它 = 停止服务。
echo.
echo --------------------------------------------------
"!PY!" run.py --port auto --open
echo --------------------------------------------------
echo.
echo 服务已停止。
pause
