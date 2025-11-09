#!/bin/bash
# 部署轻量级模式 - 快速更新脚本

echo "==========================================="
echo "🚀 PureClip - 轻量级模式部署"
echo "==========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用root用户运行此脚本"
    echo "   使用: sudo bash deploy_lightweight_mode.sh"
    exit 1
fi

# 1. 显示更新说明
echo "📋 更新内容："
echo "  ✅ 从重型模式改为轻量级模式"
echo "  ✅ 不再下载、处理、存储视频"
echo "  ✅ 直接返回原平台CDN的无水印视频URL"
echo "  ✅ 响应时间从分钟级降低到秒级"
echo "  ✅ 节省100%存储空间和带宽"
echo ""

# 2. 确认
read -p "是否继续部署？(y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 部署已取消"
    exit 1
fi

echo ""
echo "🔄 开始部署..."
echo ""

# 3. 检查服务状态
echo "📊 检查当前服务状态..."
echo ""

if systemctl is-active --quiet pureclip-celery; then
    echo "  ✅ Celery服务运行中"
    CELERY_RUNNING=true
else
    echo "  ❌ Celery服务未运行"
    CELERY_RUNNING=false
fi

if systemctl is-active --quiet pureclip-api; then
    echo "  ✅ FastAPI服务运行中"
    API_RUNNING=true
else
    echo "  ❌ FastAPI服务未运行"
    API_RUNNING=false
fi

echo ""

# 4. 备份配置（可选）
echo "📦 备份当前配置..."
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

if [ -d "backend_watermark" ]; then
    cp -r backend_watermark/celery_app/tasks.py $BACKUP_DIR/tasks.py.bak 2>/dev/null || true
    echo "  ✅ 已备份到: $BACKUP_DIR"
else
    echo "  ⚠️  backend_watermark目录不存在，跳过备份"
fi

echo ""

# 5. 重启Celery
echo "🔄 重启Celery服务..."
if $CELERY_RUNNING; then
    systemctl restart pureclip-celery
    
    # 等待服务启动
    sleep 3
    
    if systemctl is-active --quiet pureclip-celery; then
        echo "  ✅ Celery服务重启成功"
    else
        echo "  ❌ Celery服务重启失败"
        echo "  查看日志: journalctl -u pureclip-celery -n 50"
        exit 1
    fi
else
    echo "  ⚠️  Celery服务未运行，尝试启动..."
    systemctl start pureclip-celery
    
    sleep 3
    
    if systemctl is-active --quiet pureclip-celery; then
        echo "  ✅ Celery服务启动成功"
    else
        echo "  ❌ Celery服务启动失败"
        exit 1
    fi
fi

echo ""

# 6. 重启FastAPI
echo "🔄 重启FastAPI服务..."
if $API_RUNNING; then
    systemctl restart pureclip-api
    
    # 等待服务启动
    sleep 3
    
    if systemctl is-active --quiet pureclip-api; then
        echo "  ✅ FastAPI服务重启成功"
    else
        echo "  ❌ FastAPI服务重启失败"
        echo "  查看日志: journalctl -u pureclip-api -n 50"
        exit 1
    fi
else
    echo "  ⚠️  FastAPI服务未运行，尝试启动..."
    systemctl start pureclip-api
    
    sleep 3
    
    if systemctl is-active --quiet pureclip-api; then
        echo "  ✅ FastAPI服务启动成功"
    else
        echo "  ❌ FastAPI服务启动失败"
        exit 1
    fi
fi

echo ""

# 7. 检查服务状态
echo "🧪 验证服务状态..."
echo ""

sleep 2

if systemctl is-active --quiet pureclip-celery; then
    echo "  ✅ Celery: 运行中"
else
    echo "  ❌ Celery: 未运行"
fi

if systemctl is-active --quiet pureclip-api; then
    echo "  ✅ FastAPI: 运行中"
else
    echo "  ❌ FastAPI: 未运行"
fi

echo ""

# 8. 测试API
echo "🧪 测试API响应..."
echo ""

API_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/health 2>/dev/null || echo "000")

if [ "$API_TEST" = "200" ]; then
    echo "  ✅ API健康检查通过"
elif [ "$API_TEST" = "000" ]; then
    echo "  ⚠️  无法连接到API（可能是health endpoint不存在）"
    echo "  尝试访问: curl http://localhost:8001/docs"
else
    echo "  ⚠️  API返回状态码: $API_TEST"
fi

echo ""

# 9. 显示日志命令
echo "==========================================="
echo "✅ 部署完成！"
echo "==========================================="
echo ""
echo "📊 查看实时日志："
echo ""
echo "  Celery日志:"
echo "    journalctl -u pureclip-celery -f"
echo ""
echo "  FastAPI日志:"
echo "    journalctl -u pureclip-api -f"
echo ""
echo "🧪 测试命令："
echo ""
echo "  提交任务:"
echo '    curl -X POST https://api.pureclip.arbismart.cloud/api/tasks \'
echo '      -H "Content-Type: application/json" \'
echo "      -d '{\"url\": \"https://v.douyin.com/6YWKa6_haf8/\", \"media_type\": \"video\", \"method\": \"crop\", \"user_id\": \"test_user\"}'"
echo ""
echo "  查询任务:"
echo "    curl https://api.pureclip.arbismart.cloud/api/tasks/{task_id}"
echo ""
echo "📖 更多信息："
echo "  查看: LIGHTWEIGHT_MODE.md"
echo ""
echo "🎉 预期效果："
echo "  ✅ 响应时间: 2-5秒（之前是1-5分钟）"
echo "  ✅ 返回URL: 原平台CDN直链（如百度、抖音）"
echo "  ✅ 不再需要MinIO存储"
echo "  ✅ 节省100%存储空间"
echo ""
echo "==========================================="

