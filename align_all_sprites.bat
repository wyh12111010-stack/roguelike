@echo off
chcp 65001 >nul
echo ========================================
echo Align Sprites
echo ========================================
echo.

py tools\align_sprites.py nanobanana_in\

echo.
echo Done!
pause
