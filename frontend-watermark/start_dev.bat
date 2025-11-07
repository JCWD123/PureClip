@echo off
chcp 65001 >nul
cls

echo =========================================
echo   PureClip 去水印小程序 - 开发启动
echo =========================================
echo.

REM 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo × Node.js未安装，请先安装Node.js 16+
    pause
    exit /b 1
)
echo ✓ Node.js已安装

REM 检查pnpm
pnpm --version >nul 2>&1
if errorlevel 1 (
    echo × pnpm未安装，正在安装...
    npm install -g pnpm
)
echo ✓ pnpm已安装

REM 检查依赖
if not exist "node_modules" (
    echo × 依赖未安装，正在安装...
    pnpm install
) else (
    echo ✓ 依赖已安装
)

echo.
echo 请选择启动模式：
echo 1) H5开发模式 (浏览器)
echo 2) 微信小程序开发模式
echo.
set /p option=请输入选项 [1-2]: 

if "%option%"=="1" (
    echo.
    echo 启动H5开发模式...
    echo 浏览器访问: http://localhost:3000
    echo.
    pnpm dev:h5
) else if "%option%"=="2" (
    echo.
    echo 启动微信小程序开发模式...
    echo 请使用微信开发者工具打开 dist 目录
    echo.
    pnpm dev:weapp
) else (
    echo 无效选项
    pause
    exit /b 1
)

pause


