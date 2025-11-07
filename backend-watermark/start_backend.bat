@echo off
chcp 65001 >nul
cls

echo =========================================
echo   PureClip 去水印服务 - 后端启动
echo =========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo × Python未安装，请先安装Python 3.8+
    pause
    exit /b 1
)
echo ✓ Python已安装

REM 检查依赖
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo × FastAPI未安装，正在安装依赖...
    pip install -r requirements.txt
) else (
    echo ✓ 依赖已安装
)

REM 检查Redis
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo ⚠ Redis连接失败，请确保Redis正在运行
) else (
    echo ✓ Redis连接正常
)

echo.
echo =========================================
echo 启动FastAPI服务...
echo =========================================
echo.

REM 设置环境变量
set PYTHONPATH=%PYTHONPATH%;%CD%\..

REM 启动FastAPI
python app.py

pause


