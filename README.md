# 故事生成工作流

这是一个基于 LLM 的故事生成工作流系统，可以生成完整的故事元素包括角色、背景、梦境、条件和情境等。

## 📋 项目特性

- 🚀 使用 **uv** 进行快速依赖管理
- 🎯 基于 **LangChain** 和 **OpenAI** 的 AI 工作流
- 🌐 **Streamlit** 提供的现代化 Web 界面
- 📦 使用 **pyproject.toml** 的标准化项目配置
- 🐍 支持 **Python 3.12+**

## 🛠️ 安装要求

- Python 3.12 或更高版本
- [uv](https://github.com/astral-sh/uv) 包管理工具

### 安装 uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 pip
pip install uv

# 或使用 Homebrew (macOS)
brew install uv
```

## 🚀 快速开始

### 1. 克隆项目并安装依赖

```bash
git clone <your-repo-url>
cd project_netease

# 使用 uv 创建虚拟环境并安装依赖
uv sync
```

### 2. 配置环境变量

复制环境变量示例文件并配置你的 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，添加你的 OpenAI API 密钥

## 🎮 运行方式

### 方法 1: 命令行方式
```bash
uv run workflow.py
```

### 方法 2: Web 界面方式（推荐）
```bash
uv run streamlit run app_workflow.py
```

然后在浏览器中打开 `http://localhost:8501` 访问 Web 界面。

## 🌐 Web 界面功能

Web 界面提供了一个可视化的工作流，包含以下步骤：

1. **生成灵魂和主题** - 并行生成故事的核心灵魂和主题
2. **生成背景** - 基于主题生成故事背景
3. **生成角色** - 基于主题和背景生成角色
4. **生成梦境** - 生成真实和表面两种梦境
5. **生成条件** - 基于梦境生成相应的条件
6. **生成情境** - 基于所有前置元素生成当前情境
7. **生成情境选项** - 生成多个可选择的行动方案

每个步骤都有独立的生成按钮，支持按顺序逐步生成内容，实时查看生成结果。

## 🔧 开发指南

### 添加新依赖

```bash
# 添加运行时依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name

# 更新所有依赖到最新版本
uv lock --upgrade
uv sync
```

### 项目结构

```
project_netease/
├── app_workflow.py      # Streamlit Web 应用
├── workflow.py          # 命令行工作流
├── prompt_config.py     # 提示词配置
├── llm/                 # LLM 相关模块
│   ├── role/           # 角色相关
│   ├── scene/          # 场景相关
│   └── story/          # 故事相关
├── pyproject.toml      # 项目配置和依赖
├── uv.lock            # 锁定的依赖版本
└── .env               # 环境变量（不提交）
```