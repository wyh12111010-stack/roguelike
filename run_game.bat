@echo off
chcp 65001 >nul
echo ========================================
echo Run Game
echo ========================================
echo.

py main.py

if errorlevel 1 (
    echo.
    echo Game failed to start!
    pause
)
