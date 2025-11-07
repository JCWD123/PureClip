@echo off
chcp 65001 >nul
cls

echo =========================================
echo   PureClip - Celery Worker启动
echo =========================================
echo.

REM 检查Redis
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo × Redis连接失败，请确保Redis正在运行
    pause
    exit /b 1
) else (
    echo ✓ Redis连接正常
)

echo.
echo 启动Celery Worker...
echo.

REM 设置环境变量
set PYTHONPATH=%PYTHONPATH%;%CD%\..

REM 启动Celery Worker
celery -A backend_watermark.celery_app.celery worker --loglevel=info --concurrency=4 --pool=solo

pause


