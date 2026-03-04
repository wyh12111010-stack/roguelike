@echo off
cd /d "%~dp0"

echo 当前目录: %cd%
echo.
echo 检查 Python...
python --version 2>&1
if errorlevel 1 (
    echo python 未找到，尝试 py...
    py --version 2>&1
)
echo.
echo 安装依赖（如有报错请忽略）...
pip install pygame pymunk
echo.
echo 运行游戏...
python main.py
if errorlevel 1 py main.py

echo.
echo 退出码: %errorlevel%
pause
