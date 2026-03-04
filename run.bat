@echo off
cd /d "%~dp0"

python -m pip install pygame pymunk -q 2>nul
python main.py

pause
