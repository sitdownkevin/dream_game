.PHONY: help install dev run clean test format lint

# 默认目标
help:
	@echo "🌙 梦境之旅 - 互动故事游戏"
	@echo "============================="
	@echo ""
	@echo "可用命令:"
	@echo "  install   安装项目依赖"
	@echo "  dev       安装开发依赖"
	@echo "  run       启动游戏服务器"
	@echo "  clean     清理环境"
	@echo "  test      运行测试"
	@echo "  format    格式化代码"
	@echo "  lint      代码检查"
	@echo ""

# 安装依赖
install:
	@echo "📦 安装项目依赖..."
	uv sync

# 安装开发依赖
dev:
	@echo "🛠️ 安装开发依赖..."
	uv sync --dev

# 启动游戏
run:
	@echo "🚀 启动梦境之旅游戏..."
	@echo "📍 访问地址: http://localhost:5001"
	@echo ""
	uv run python run_game.py

# 清理环境
clean:
	@echo "🧹 清理环境..."
	rm -rf .venv
	uv cache clean

# 运行测试
test:
	@echo "🧪 运行测试..."
	uv run pytest

# 格式化代码
format:
	@echo "✨ 格式化代码..."
	uv run black .
	uv run isort .

# 代码检查
lint:
	@echo "🔍 代码检查..."
	uv run flake8 .

# 查看依赖树
tree:
	@echo "📋 依赖树:"
	uv tree

# 检查过期依赖
outdated:
	@echo "📊 检查过期依赖..."
	uv pip list --outdated 