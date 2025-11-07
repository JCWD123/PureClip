#!/bin/bash
# ArbiSmart 后端生产模式启动脚本
# 使用方法: bash start_prod.sh

echo "🚀 启动 medai 后端服务 (生产模式)"
echo "-----------------------------------"
echo "✅ 热重载: 已禁用"
echo "📁 工作目录: $(pwd)"
echo "🐍 Python: $(python --version 2>&1)"
echo "-----------------------------------"

# 确保在正确的目录
cd "$(dirname "$0")"

# 设置生产环境
export ENV=production

# 停止旧进程
echo "🛑 停止旧进程..."
pkill -f "python.*app.py"
sleep 2

# 后台启动服务（无热重载）
echo "🚀 启动新进程..."
nohup python app.py > /tmp/medai_backend.log 2>&1 &

echo "-----------------------------------"
echo "✅ 服务已在后台启动"
echo "📋 进程ID: $!"
echo "📝 日志文件: /tmp/medai_backend.log"
echo ""
echo "查看日志: tail -f /tmp/medai_backend.log"
echo "停止服务: pkill -f 'python.*app.py'"
echo "-----------------------------------"





















