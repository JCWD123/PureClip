#!/bin/bash

# PureClip后端启动脚本

echo "========================================="
echo "  PureClip 去水印服务 - 后端启动"
echo "========================================="
echo ""

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python版本: $python_version"

# 检查依赖是否安装
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "× FastAPI未安装，正在安装依赖..."
    pip3 install -r requirements.txt
else
    echo "✓ 依赖已安装"
fi

# 检查MongoDB连接
echo "检查MongoDB连接..."
if ! python3 -c "from pymongo import MongoClient; MongoClient('localhost', 27017).admin.command('ping')" 2>/dev/null; then
    echo "⚠ MongoDB连接失败，请确保MongoDB正在运行"
else
    echo "✓ MongoDB连接正常"
fi

# 检查Redis连接
echo "检查Redis连接..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠ Redis连接失败，请确保Redis正在运行"
else
    echo "✓ Redis连接正常"
fi

echo ""
echo "========================================="
echo "启动FastAPI服务..."
echo "========================================="
echo ""

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."

# 启动FastAPI
python3 app.py


