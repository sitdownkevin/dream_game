.PHONY: help run clean workflow

# 默认目标
help:
	@echo "🌙 梦境之旅 - 互动故事游戏"
	@echo "============================="
	@echo ""
	@echo "可用命令:"
	@echo "  run       启动游戏服务器"
	@echo "  clean     清理环境"
	@echo ""

# 启动游戏
run:
	@echo "🚀 启动梦境之旅游戏..."
	@echo "📍 访问地址: http://localhost:5001"
	@echo ""
	uv run python run_game.py

# 启动 Workflow
workflow:
	@echo "开始生成 Workflow..."
	uv run python workflow.py

# 清理环境
clean:
	@echo "🧹 清理环境..."
	rm -rf .venv
	uv cache clean

# 查看依赖树
tree:
	@echo "📋 依赖树:"
	uv tree

# 检查过期依赖
outdated:
	@echo "📊 检查过期依赖..."
	uv pip list --outdated 