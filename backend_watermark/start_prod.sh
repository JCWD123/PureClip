#!/bin/bash

# PureClip 后端生产模式启动脚本
# 使用方法: bash start_prod.sh

echo "🚀 启动 PureClip 后端服务 (生产模式)"
echo "-----------------------------------"
echo "✅ 热重载: 已禁用"
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
pkill -f "uvicorn backend_watermark.app:app"
pkill -f "python.*backend_watermark/app.py"
sleep 2

# 检查端口占用
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口 8001 仍被占用，强制停止..."
    lsof -ti:8001 | xargs kill -9 2>/dev/null
    sleep 1
fi

# 后台启动服务（无热重载）
echo "🚀 启动新进程..."
nohup uvicorn backend_watermark.app:app \
    --host 0.0.0.0 \
    --port 8001 \
    --workers 2 \
    > /tmp/pureclip_backend.log 2>&1 &

PID=$!

sleep 2

# 验证服务是否启动成功
if ps -p $PID > /dev/null; then
    echo "-----------------------------------"
    echo "✅ 服务已在后台启动"
    echo "📋 进程ID: $PID"
    echo "📝 日志文件: /tmp/pureclip_backend.log"
    echo "🌐 服务地址: http://0.0.0.0:8001"
    echo ""
    echo "查看日志: tail -f /tmp/pureclip_backend.log"
    echo "停止服务: pkill -f 'uvicorn backend_watermark.app:app'"
    echo "-----------------------------------"
else
    echo "-----------------------------------"
    echo "❌ 服务启动失败"
    echo "📝 查看日志: cat /tmp/pureclip_backend.log"
    echo "-----------------------------------"
    exit 1
fi

