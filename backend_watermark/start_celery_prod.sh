#!/bin/bash

# PureClip Celery 生产模式启动脚本
# 使用方法: bash start_celery_prod.sh

echo "🚀 启动 PureClip Celery Worker (生产模式)"
echo "-----------------------------------"
echo "📁 工作目录: $(pwd)"
echo "🐍 Python: $(python --version 2>&1)"
echo "-----------------------------------"

# 切换到项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "📂 项目根目录: $(pwd)"
echo "-----------------------------------"

# 设置生产环境
export ENV=production

# 停止旧进程
echo "🛑 停止旧进程..."
pkill -f "celery -A backend_watermark.celery_app.celery worker"
sleep 2

# 后台启动 Celery Worker
echo "🚀 启动新进程..."
nohup celery -A backend_watermark.celery_app.celery worker \
    --loglevel=info \
    --concurrency=2 \
    > /tmp/pureclip_celery.log 2>&1 &

PID=$!

sleep 3

# 验证服务是否启动成功
if ps -p $PID > /dev/null; then
    echo "-----------------------------------"
    echo "✅ Celery Worker 已在后台启动"
    echo "📋 进程ID: $PID"
    echo "📝 日志文件: /tmp/pureclip_celery.log"
    echo "🔧 并发数: 2"
    echo ""
    echo "查看日志: tail -f /tmp/pureclip_celery.log"
    echo "停止服务: pkill -f 'celery -A backend_watermark.celery_app.celery worker'"
    echo "-----------------------------------"
else
    echo "-----------------------------------"
    echo "❌ Celery Worker 启动失败"
    echo "📝 查看日志: cat /tmp/pureclip_celery.log"
    echo "-----------------------------------"
    exit 1
fi

