#!/bin/bash

# Celery Worker启动脚本

echo "========================================="
echo "  PureClip - Celery Worker启动"
echo "========================================="
echo ""

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."

# 检查Redis连接
echo "检查Redis连接..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "× Redis连接失败，请确保Redis正在运行"
    exit 1
else
    echo "✓ Redis连接正常"
fi

echo ""
echo "启动Celery Worker..."
echo ""

# 启动Celery Worker
celery -A backend_watermark.celery_app.celery worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=100


