#!/bin/bash

# PureClip 停止所有服务脚本
# 使用方法: bash stop_services.sh

echo "🛑 停止 PureClip 所有服务"
echo "-----------------------------------"

# 切换到项目根目录（如果需要）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 停止 FastAPI
echo "🛑 停止 FastAPI..."
pkill -f "uvicorn backend_watermark.app:app"
sleep 1

# 停止 Celery
echo "🛑 停止 Celery Worker..."
pkill -f "celery -A backend_watermark.celery_app.celery worker"
sleep 1

# 强制停止（如果还在运行）
if pgrep -f "uvicorn backend_watermark.app:app" > /dev/null; then
    echo "⚠️  强制停止 FastAPI..."
    pkill -9 -f "uvicorn backend_watermark.app:app"
fi

if pgrep -f "celery -A backend_watermark.celery_app.celery worker" > /dev/null; then
    echo "⚠️  强制停止 Celery..."
    pkill -9 -f "celery -A backend_watermark.celery_app.celery worker"
fi

# 检查端口占用
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  清理端口 8001..."
    lsof -ti:8001 | xargs kill -9 2>/dev/null
fi

echo "-----------------------------------"
echo "✅ 所有服务已停止"
echo "-----------------------------------"

# 显示当前状态
echo ""
echo "📊 当前状态:"
if pgrep -f "uvicorn backend_watermark.app:app" > /dev/null; then
    echo "  ❌ FastAPI: 仍在运行"
else
    echo "  ✅ FastAPI: 已停止"
fi

if pgrep -f "celery -A backend_watermark.celery_app.celery worker" > /dev/null; then
    echo "  ❌ Celery: 仍在运行"
else
    echo "  ✅ Celery: 已停止"
fi

