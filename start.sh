#!/bin/bash

echo "🌙 梦境之旅 - 互动故事游戏"
echo "================================="
echo ""

# 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ uv 未安装，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv 安装完成"
fi

echo "📦 同步依赖..."
uv sync

echo ""
echo "🚀 启动游戏服务器..."
echo "📍 访问地址: http://localhost:5001"
echo "🔄 使用 Ctrl+C 停止服务"
echo ""

uv run python run_game.py 