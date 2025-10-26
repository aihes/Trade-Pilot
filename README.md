# Trade-Pilot

一个基于 AI Agent 的量化交易实验项目，用于探索和验证量化交易策略的可行性。

## 项目概述

Trade-Pilot 是一个智能交易代理系统，通过集成 AI 能力和多源市场信号，在 Hyperliquid 平台上执行合约交易操作。

## 核心功能

- **AI 驱动决策**: 集成 OpenRouter 平台的 AI 模型，实现智能交易决策
- **合约交易**: 在 Hyperliquid 平台上执行永续合约交易
- **多源信号**: 整合新闻信息、技术指标等多种交易信号源
- **策略验证**: 用于测试和验证量化交易策略的有效性

## 技术栈

- **交易执行**: [CCXT](https://github.com/ccxt/ccxt) - 统一的加密货币交易 API
- **AI 框架**: LangChain + LangGraph - AI Agent 开发框架
- **AI 模型**: OpenRouter - 多模型 AI 接入平台
- **交易平台**: Hyperliquid - 去中心化永续合约交易所
- **包管理**: UV - 快速的 Python 包管理器

## 快速开始

### 1. 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填写 API 密钥
```

### 3. 运行

```bash
# 启动交互式 Agent
uv run trade-pilot

# 或运行示例
uv run python examples/basic_usage.py
```

详细使用说明请查看 [快速开始文档](docs/QUICKSTART.md)。

## 项目结构

```
Trade-Pilot/
├── src/trade_pilot/          # 核心代码
│   ├── hyperliquid_client.py # Hyperliquid 客户端封装
│   ├── agent.py              # AI Agent 实现
│   └── tools.py              # LangChain 工具封装
├── examples/                 # 使用示例
├── docs/                     # 文档
│   ├── QUICKSTART.md         # 快速开始
│   └── PROJECT_SUMMARY.md    # 项目总结
├── .env.example              # 环境变量模板
└── pyproject.toml            # 项目配置
```

## 可用工具

Agent 具备以下交易能力：

1. **下单** - 市价单和限价单
2. **取消订单** - 取消指定订单或所有订单
3. **查询订单** - 查询订单状态和未成交订单
4. **持仓管理** - 查看持仓和一键平仓
5. **行情查询** - 获取实时价格和订单簿

## 文档

- [快速开始](docs/QUICKSTART.md) - 安装和使用指南
- [项目总结](docs/PROJECT_SUMMARY.md) - 详细的技术文档和开发计划

## 项目状态

🚧 **开发中** - 这是一个实验性项目，用于探索 AI 在量化交易中的应用可能性。

### 已完成

- ✅ 项目框架搭建
- ✅ CCXT 集成
- ✅ LangChain/LangGraph 集成
- ✅ 基础交易工具实现
- ✅ AI Agent 实现

### 计划中

- 🔲 集成 Jina AI 新闻搜索
- 🔲 技术指标分析
- 🔲 策略回测系统
- 🔲 风险管理模块

## 免责声明

⚠️ **重要提示**：

- 本项目仅用于学习和研究目的
- 加密货币交易存在高风险，可能导致资金损失
- 请先在测试网充分测试
- 实盘交易需谨慎，风险自负

## License

MIT

