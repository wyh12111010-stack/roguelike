@echo off
cd /d "%~dp0"
python main.py > start_log.txt 2>&1
echo Done. Check start_log.txt
pause
