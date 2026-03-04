@echo off
cd /d "%~dp0"
python -m tools.balance_test --runs 5
echo.
python -m tools.balance_test --runs 5 --survival
pause
