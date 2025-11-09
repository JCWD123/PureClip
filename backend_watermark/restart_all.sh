#!/bin/bash

# PureClip 一键重启所有服务脚本
# 使用方法: bash restart_all.sh

echo "==========================================="
echo "🔄 重启 PureClip 所有服务"
echo "==========================================="
echo ""

# 确保在正确的目录
cd "$(dirname "$0")"

# 1. 停止所有服务
echo "📋 步骤 1/3: 停止现有服务"
echo "-----------------------------------"
bash stop_services.sh
echo ""

# 等待一下
sleep 2

# 2. 启动 Celery
echo "📋 步骤 2/3: 启动 Celery Worker"
echo "-----------------------------------"
bash start_celery_prod.sh
echo ""

# 等待 Celery 完全启动
sleep 3

# 3. 启动 FastAPI
echo "📋 步骤 3/3: 启动 FastAPI"
echo "-----------------------------------"
bash start_prod.sh
echo ""

# 等待 FastAPI 完全启动
sleep 3

# 验证服务状态
echo "==========================================="
echo "📊 服务状态检查"
echo "==========================================="
echo ""

CELERY_RUNNING=$(pgrep -f "celery -A backend_watermark.celery_app.celery worker" | wc -l)
API_RUNNING=$(pgrep -f "uvicorn backend_watermark.app:app" | wc -l)

if [ "$CELERY_RUNNING" -gt 0 ]; then
    echo "  ✅ Celery Worker: 运行中 ($CELERY_RUNNING 进程)"
else
    echo "  ❌ Celery Worker: 未运行"
fi

if [ "$API_RUNNING" -gt 0 ]; then
    echo "  ✅ FastAPI: 运行中 ($API_RUNNING 进程)"
else
    echo "  ❌ FastAPI: 未运行"
fi

echo ""
echo "==========================================="
echo "✅ 重启完成！"
echo "==========================================="
echo ""
echo "📝 查看日志:"
echo "  Celery: tail -f /tmp/pureclip_celery.log"
echo "  FastAPI: tail -f /tmp/pureclip_backend.log"
echo ""
echo "🧪 测试服务:"
echo "  curl http://localhost:8001/docs"
echo ""

