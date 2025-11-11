#!/bin/bash
# 即梦AI解析器更新部署脚本

echo "==========================================="
echo "🎬 即梦AI解析器升级部署"
echo "==========================================="
echo ""

# 检查是否在正确的目录
if [ ! -f "backend_watermark/services/video_parser.py" ]; then
    echo "❌ 错误: 请在项目根目录 (PureClip) 下运行此脚本"
    exit 1
fi

# 1. 检查虚拟环境
echo "📋 步骤 1/4: 检查虚拟环境"
echo "-----------------------------------"

if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "⚠️  虚拟环境未激活"
    echo "请先运行: conda activate PureClip"
    exit 1
else
    echo "✅ 虚拟环境: $CONDA_DEFAULT_ENV"
fi

echo ""

# 2. 安装新依赖
echo "📋 步骤 2/4: 安装新依赖"
echo "-----------------------------------"

echo "📦 安装 lxml..."
pip install lxml==5.1.0 -q

if [ $? -eq 0 ]; then
    echo "✅ lxml 安装成功"
else
    echo "❌ lxml 安装失败"
    echo "尝试手动安装: pip install lxml==5.1.0"
    exit 1
fi

echo "📦 安装 httpx..."
pip install httpx==0.27.0 -q

if [ $? -eq 0 ]; then
    echo "✅ httpx 安装成功"
else
    echo "❌ httpx 安装失败"
    echo "尝试手动安装: pip install httpx==0.27.0"
    exit 1
fi

# 验证安装
echo ""
echo "🔍 验证依赖安装..."
python -c "from lxml import etree; print('  ✅ lxml版本:', etree.__version__)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  ❌ lxml导入失败"
    exit 1
fi

python -c "import httpx; print('  ✅ httpx版本:', httpx.__version__)" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  ❌ httpx导入失败"
    exit 1
fi

echo ""

# 3. 检查代码语法
echo "📋 步骤 3/4: 检查代码语法"
echo "-----------------------------------"

python -m py_compile backend_watermark/services/video_parser.py 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ 代码语法正确"
else
    echo "❌ 代码语法错误"
    python -m py_compile backend_watermark/services/video_parser.py
    exit 1
fi

echo ""

# 4. 重启服务
echo "📋 步骤 4/4: 重启服务"
echo "-----------------------------------"

cd backend_watermark

if [ -f "restart_all.sh" ]; then
    echo "🔄 使用 restart_all.sh 重启服务..."
    bash restart_all.sh
else
    echo "⚠️  restart_all.sh 不存在，手动重启服务"
    
    # 停止旧服务
    echo "🛑 停止旧服务..."
    pkill -f "celery.*worker"
    pkill -f "uvicorn.*backend_watermark.app:app"
    sleep 2
    
    # 启动新服务
    cd ..
    
    echo "🚀 启动 Celery Worker..."
    nohup celery -A backend_watermark.celery_app.celery worker --loglevel=info > /tmp/pureclip_celery.log 2>&1 &
    
    sleep 3
    
    echo "🚀 启动 FastAPI..."
    nohup uvicorn backend_watermark.app:app --host 0.0.0.0 --port 8001 > /tmp/pureclip_backend.log 2>&1 &
    
    sleep 2
fi

echo ""

# 5. 检查服务状态
echo "==========================================="
echo "📊 服务状态检查"
echo "==========================================="

CELERY_PID=$(pgrep -f "celery.*worker")
FASTAPI_PID=$(pgrep -f "uvicorn.*backend_watermark.app:app")

if [ -n "$CELERY_PID" ]; then
    echo "  ✅ Celery Worker: 运行中 (PID: $CELERY_PID)"
else
    echo "  ❌ Celery Worker: 未运行"
fi

if [ -n "$FASTAPI_PID" ]; then
    echo "  ✅ FastAPI: 运行中 (PID: $FASTAPI_PID)"
else
    echo "  ❌ FastAPI: 未运行"
fi

echo ""

# 6. 创建测试脚本
echo "==========================================="
echo "🧪 创建测试脚本"
echo "==========================================="

cat > test_jimeng.py << 'EOF'
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""即梦AI解析器测试脚本"""
import sys
sys.path.insert(0, '/root/PureClip')

from backend_watermark.services.video_parser import get_video_parser

def test_jimeng():
    """测试即梦AI解析"""
    print("=" * 50)
    print("🧪 即梦AI解析器测试")
    print("=" * 50)
    print()
    
    # 测试URL
    test_url = "https://jimeng.jianying.com/s/bYeEyb6ThwU/?t=210"
    
    print(f"📎 测试URL: {test_url}")
    print()
    
    # 获取解析器
    parser = get_video_parser()
    
    # 解析URL
    print("🔄 开始解析...")
    result = parser.parse(test_url)
    
    # 打印结果
    print()
    print("=" * 50)
    print("📊 解析结果")
    print("=" * 50)
    print(f"✅ 解析成功: {result['success']}")
    print(f"🏷️  平台: {result['platform']}")
    print(f"📝 标题: {result['title']}")
    
    if result['video_url']:
        print(f"🎥 视频URL: {result['video_url'][:80]}...")
    else:
        print(f"🎥 视频URL: None")
    
    if result['cover']:
        print(f"🖼️  封面: {result['cover'][:80]}...")
    else:
        print(f"🖼️  封面: None")
    
    if result['error']:
        print(f"❌ 错误: {result['error']}")
    
    print("=" * 50)
    
    return result['success']

if __name__ == '__main__':
    success = test_jimeng()
    sys.exit(0 if success else 1)
EOF

chmod +x test_jimeng.py

echo "✅ 测试脚本已创建: test_jimeng.py"
echo ""

# 7. 完成提示
echo "==========================================="
echo "✅ 部署完成！"
echo "==========================================="
echo ""
echo "📝 下一步操作:"
echo ""
echo "1. 查看Celery日志:"
echo "   tail -f /tmp/pureclip_celery.log | grep -E '即梦|jimeng'"
echo ""
echo "2. 测试即梦AI解析:"
echo "   python test_jimeng.py"
echo ""
echo "3. 使用API测试:"
echo "   curl -X POST http://localhost:8001/api/tasks \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"url\": \"https://jimeng.jianying.com/s/bYeEyb6ThwU/?t=210\", \"media_type\": \"video\", \"method\": \"crop\", \"user_id\": \"test\"}'"
echo ""
echo "4. 查看完整文档:"
echo "   cat JIMENG_PARSER_UPDATE.md"
echo ""
echo "==========================================="

