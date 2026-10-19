@echo off
rem --------------------------------------------------------------
rem  Double-click this to share on the local network.
rem  It is just a shortcut for:  start.bat lan
rem
rem  Why a separate file: start.bat decides its mode from %1, and a
rem  double-click passes no argument - so double-clicking start.bat always
rem  gives you the private 127.0.0.1 mode, which colleagues cannot reach.
rem
rem  Guests are READ-ONLY (browse cases only). To let them generate too,
rem  run "start.bat lan write" from a terminal instead.
rem --------------------------------------------------------------
setlocal
cd /d "%~dp0"
call "%~dp0start.bat" lan
