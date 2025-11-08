#!/bin/bash

# PureClip前端开发启动脚本

echo "========================================="
echo "  PureClip 去水印小程序 - 开发启动"
echo "========================================="
echo ""

# 检查Node.js版本
node_version=$(node --version)
echo "✓ Node.js版本: $node_version"

# 检查pnpm是否安装
if ! command -v pnpm &> /dev/null; then
    echo "× pnpm未安装，正在安装..."
    npm install -g pnpm
else
    pnpm_version=$(pnpm --version)
    echo "✓ pnpm版本: $pnpm_version"
fi

# 检查依赖是否安装
if [ ! -d "node_modules" ]; then
    echo "× 依赖未安装，正在安装..."
    pnpm install
else
    echo "✓ 依赖已安装"
fi

echo ""
echo "请选择启动模式："
echo "1) H5开发模式 (浏览器)"
echo "2) 微信小程序开发模式"
echo ""
read -p "请输入选项 [1-2]: " option

case $option in
    1)
        echo ""
        echo "启动H5开发模式..."
        echo "浏览器访问: http://localhost:3000"
        echo ""
        pnpm dev:h5
        ;;
    2)
        echo ""
        echo "启动微信小程序开发模式..."
        echo "请使用微信开发者工具打开 dist 目录"
        echo ""
        pnpm dev:weapp
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac



