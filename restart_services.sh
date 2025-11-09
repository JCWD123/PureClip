#!/bin/bash
# 一键重启服务脚本

echo "🔄 重启 PureClip 服务..."
echo ""

# 1. 停止现有进程
echo "🛑 停止现有进程..."

# 停止 Celery
CELERY_PIDS=$(ps aux | grep "celery -A backend_watermark" | grep -v grep | awk '{print $2}')
if [ -n "$CELERY_PIDS" ]; then
    echo "  停止 Celery (PIDs: $CELERY_PIDS)"
    kill $CELERY_PIDS 2>/dev/null
    sleep 2
fi

# 停止 FastAPI
UVICORN_PIDS=$(ps aux | grep "uvicorn backend_watermark.app:app" | grep -v grep | awk '{print $2}')
if [ -n "$UVICORN_PIDS" ]; then
    echo "  停止 FastAPI (PIDs: $UVICORN_PIDS)"
    kill $UVICORN_PIDS 2>/dev/null
    sleep 2
fi

# 强制停止（如果还在运行）
CELERY_PIDS=$(ps aux | grep "celery -A backend_watermark" | grep -v grep | awk '{print $2}')
if [ -n "$CELERY_PIDS" ]; then
    echo "  强制停止 Celery"
    kill -9 $CELERY_PIDS 2>/dev/null
fi

UVICORN_PIDS=$(ps aux | grep "uvicorn backend_watermark.app:app" | grep -v grep | awk '{print $2}')
if [ -n "$UVICORN_PIDS" ]; then
    echo "  强制停止 FastAPI"
    kill -9 $UVICORN_PIDS 2>/dev/null
fi

echo "  ✅ 已停止所有进程"
echo ""

# 2. 检查虚拟环境
if [[ "$CONDA_DEFAULT_ENV" != "PureClip" ]]; then
    echo "⚠️  请先激活虚拟环境: conda activate PureClip"
    exit 1
fi

# 3. 启动服务
echo "🚀 启动服务..."
echo ""

# 创建日志目录
mkdir -p logs

# 启动 Celery（后台运行）
echo "  启动 Celery Worker..."
nohup celery -A backend_watermark.celery_app.celery worker --loglevel=info > logs/celery.log 2>&1 &
CELERY_PID=$!
echo "  ✅ Celery 已启动 (PID: $CELERY_PID)"

# 等待一下
sleep 2

# 启动 FastAPI（后台运行）
echo "  启动 FastAPI..."
nohup uvicorn backend_watermark.app:app --host 0.0.0.0 --port 8001 > logs/uvicorn.log 2>&1 &
API_PID=$!
echo "  ✅ FastAPI 已启动 (PID: $API_PID)"

echo ""
echo "==========================================="
echo "✅ 服务启动完成！"
echo "==========================================="
echo ""

# 等待服务完全启动
sleep 3

# 4. 验证服务状态
echo "🔍 验证服务状态..."
echo ""

CELERY_RUNNING=$(ps aux | grep "celery -A backend_watermark" | grep -v grep | wc -l)
API_RUNNING=$(ps aux | grep "uvicorn backend_watermark.app:app" | grep -v grep | wc -l)

if [ "$CELERY_RUNNING" -gt 0 ]; then
    echo "  ✅ Celery: 运行中"
else
    echo "  ❌ Celery: 未运行"
fi

if [ "$API_RUNNING" -gt 0 ]; then
    echo "  ✅ FastAPI: 运行中"
else
    echo "  ❌ FastAPI: 未运行"
fi

echo ""
echo "📊 查看日志："
echo "  Celery: tail -f logs/celery.log"
echo "  FastAPI: tail -f logs/uvicorn.log"
echo ""
echo "🧪 测试命令："
echo '  curl -X POST https://api.pureclip.arbismart.cloud/api/tasks \'
echo '    -H "Content-Type: application/json" \'
echo "    -d '{\"url\": \"https://v.douyin.com/6YWKa6_haf8/\", \"media_type\": \"video\", \"method\": \"crop\", \"user_id\": \"test\"}'"
echo ""

