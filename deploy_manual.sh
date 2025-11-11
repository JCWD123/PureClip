#!/bin/bash
# 手动部署脚本 - 适用于非systemd管理的服务

echo "==========================================="
echo "🚀 PureClip - 轻量级模式部署（手动模式）"
echo "==========================================="
echo ""


echo "📋 更新内容："
echo "  ✅ 从重型模式改为轻量级模式"
echo "  ✅ 不再下载、处理、存储视频"
echo "  ✅ 直接返回原平台CDN的无水印视频URL"
echo "  ✅ 响应时间从分钟级降低到秒级"
echo ""

# 确认
read -p "是否继续部署？(y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 部署已取消"
    exit 1
fi

echo ""
echo "🔄 开始部署..."
echo ""

# 1. 检查当前进程
echo "📊 检查当前运行的进程..."
echo ""

CELERY_PIDS=$(ps aux | grep "celery -A backend_watermark" | grep -v grep | awk '{print $2}')
UVICORN_PIDS=$(ps aux | grep "uvicorn backend_watermark.app:app" | grep -v grep | awk '{print $2}')

if [ -n "$CELERY_PIDS" ]; then
    echo "  ✅ Celery进程运行中 (PIDs: $CELERY_PIDS)"
    CELERY_RUNNING=true
else
    echo "  ❌ Celery进程未运行"
    CELERY_RUNNING=false
fi

if [ -n "$UVICORN_PIDS" ]; then
    echo "  ✅ FastAPI进程运行中 (PIDs: $UVICORN_PIDS)"
    API_RUNNING=true
else
    echo "  ❌ FastAPI进程未运行"
    API_RUNNING=false
fi

echo ""

# 2. 备份配置
echo "📦 备份当前配置..."
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

if [ -f "backend_watermark/celery_app/tasks.py" ]; then
    cp backend_watermark/celery_app/tasks.py $BACKUP_DIR/tasks.py.bak
    echo "  ✅ 已备份到: $BACKUP_DIR"
else
    echo "  ⚠️  tasks.py 不存在"
fi

echo ""

# 3. 停止现有进程
if $CELERY_RUNNING; then
    echo "🛑 停止现有Celery进程..."
    for PID in $CELERY_PIDS; do
        kill $PID 2>/dev/null && echo "  ✅ 已停止进程: $PID" || echo "  ⚠️  无法停止进程: $PID"
    done
    echo ""
    echo "⏳ 等待进程完全停止..."
    sleep 3
fi

if $API_RUNNING; then
    echo "🛑 停止现有FastAPI进程..."
    for PID in $UVICORN_PIDS; do
        kill $PID 2>/dev/null && echo "  ✅ 已停止进程: $PID" || echo "  ⚠️  无法停止进程: $PID"
    done
    echo ""
    echo "⏳ 等待进程完全停止..."
    sleep 3
fi

echo ""

# 4. 验证配置文件
echo "🔍 验证配置文件..."
if [ -f "backend_watermark/config/config.yaml" ]; then
    echo "  ✅ config.yaml 存在"
    
    # 检查 iiilab 配置
    if grep -q "client_id: \"cbc1e14780805f6g\"" backend_watermark/config/config.yaml; then
        echo "  ✅ iiilab API配置正确"
    else
        echo "  ⚠️  iiilab API配置可能有问题"
    fi
else
    echo "  ❌ config.yaml 不存在"
    exit 1
fi

echo ""

# 5. 重启服务
echo "==========================================="
echo "⚠️  需要手动启动服务"
echo "==========================================="
echo ""
echo "请打开两个新的终端窗口，分别运行以下命令："
echo ""
echo "终端1 - 启动Celery:"
echo "  cd /root/PureClip"
echo "  conda activate PureClip"
echo "  celery -A backend_watermark.celery_app.celery worker --loglevel=info"
echo ""
echo "终端2 - 启动FastAPI:"
echo "  cd /root/PureClip"
echo "  conda activate PureClip"
echo "  uvicorn backend_watermark.app:app --host 0.0.0.0 --port 8001 --reload"
echo ""
echo "==========================================="
echo ""

# 6. 提供测试命令
echo "🧪 启动后测试命令："
echo ""
echo "  # 提交任务"
echo '  curl -X POST https://api.pureclip.arbismart.cloud/api/tasks \'
echo '    -H "Content-Type: application/json" \'
echo "    -d '{\"url\": \"https://v.douyin.com/6YWKa6_haf8/\", \"media_type\": \"video\", \"method\": \"crop\", \"user_id\": \"test\"}'"
echo ""
echo "  # 查询任务（2-5秒后）"
echo "  curl https://api.pureclip.arbismart.cloud/api/tasks/{task_id}"
echo ""
echo "==========================================="
echo "✅ 部署准备完成！"
echo "==========================================="
echo ""
echo "📖 预期效果："
echo "  ✅ 响应时间: 2-5秒（之前是1-5分钟）"
echo "  ✅ 返回URL: 原平台CDN直链"
echo "  ✅ Celery日志: 显示'解析成功'而不是'下载完成'"
echo ""



