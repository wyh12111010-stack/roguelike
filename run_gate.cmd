@echo off
setlocal

REM Windows CMD regression wrapper
REM Usage:
REM   run_gate.cmd quick
REM   run_gate.cmd nightly
REM   run_gate.cmd audit
REM   run_gate.cmd list

set MODE=%1
set ARGS=

if "%MODE%"=="" (
  set ARGS=--preset quick
  goto run
)

if /I "%MODE%"=="list" (
  shift
  set ARGS=--list %*
  goto run
)

if /I "%MODE%"=="quick" (
  shift
  set ARGS=--preset quick %*
  goto run
)

if /I "%MODE%"=="nightly" (
  shift
  set ARGS=--preset nightly %*
  goto run
)

if /I "%MODE%"=="audit" (
  shift
  set ARGS=--preset audit %*
  goto run
)

REM 其他参数原样透传给 tools.regression_gate（例如 --scope/--change-type）
set ARGS=%*

:run
echo Running: python -m tools.regression_gate %ARGS%
python -m tools.regression_gate %ARGS%
exit /b %ERRORLEVEL%
