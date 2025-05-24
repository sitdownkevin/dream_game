# 🚀 快速开始

## 一行命令启动

```bash
# 方式一：使用启动脚本
./start.sh

# 方式二：使用 Makefile
make run

# 方式三：使用 uv 直接运行
uv run python run_game.py
```

## 安装 uv（如果未安装）

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 常用命令

```bash
# 查看所有可用命令
make help

# 安装依赖
make install

# 启动游戏
make run

# 代码格式化
make format

# 代码检查
make lint
```

## 访问游戏

游戏启动后，打开浏览器访问：**http://localhost:5001**

---

就是这么简单！🎮✨ 