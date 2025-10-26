# Trade-Pilot 快速开始

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/aihes/Trade-Pilot.git
cd Trade-Pilot
```

### 2. 安装依赖

使用 uv 安装依赖（推荐）：

```bash
# 安装 uv（如果还没有安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv sync
```

或使用 pip：

```bash
pip install -e .
```

### 3. 配置环境变量

复制 `.env.example` 到 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# Hyperliquid API 配置
HYPERLIQUID_API_KEY=your_api_key_here
HYPERLIQUID_API_SECRET=your_api_secret_here
HYPERLIQUID_TESTNET=true

# OpenRouter API 配置
OPENROUTER_API_KEY=your_openrouter_api_key_here

# 模型配置
MODEL_NAME=anthropic/claude-3.5-sonnet
```

## 获取 API 密钥

### Hyperliquid API

1. 访问 [Hyperliquid](https://hyperliquid.xyz/)
2. 创建账户并生成 API 密钥
3. **建议先使用测试网进行测试**

### OpenRouter API

1. 访问 [OpenRouter](https://openrouter.ai/)
2. 注册账户
3. 在设置中生成 API 密钥

## 使用方法

### 方式 1: 命令行启动

```bash
# 使用 uv
uv run trade-pilot

# 或使用 python
python -m trade_pilot
```

### 方式 2: 运行示例

```bash
# 使用 uv
uv run python examples/basic_usage.py

# 或使用 python
python examples/basic_usage.py
```

### 方式 3: 在代码中使用

```python
import os
from dotenv import load_dotenv
from trade_pilot import HyperliquidClient, TradingAgent

# 加载环境变量
load_dotenv()

# 创建客户端
client = HyperliquidClient(
    api_key=os.getenv("HYPERLIQUID_API_KEY"),
    api_secret=os.getenv("HYPERLIQUID_API_SECRET"),
    testnet=True
)

# 创建 Agent
agent = TradingAgent(
    hyperliquid_client=client,
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
    model="anthropic/claude-3.5-sonnet"
)

# 使用 Agent
response = agent.run("帮我查看 BTC 的当前价格")
print(response)

# 或启动交互式聊天
agent.chat()
```

## 功能示例

### 查询行情

```
You: 帮我查看 BTC 的当前价格

Agent: 当前 BTC/USDT 的价格是 $45,123.45
```

### 查询持仓

```
You: 我现在有哪些持仓？

Agent: 您当前有以下持仓：
1. BTC/USDT:USDT - 多头 0.5 张，入场价 $44,000
2. ETH/USDT:USDT - 空头 2 张，入场价 $2,300
```

### 下单

```
You: 帮我以市价买入 0.1 张 BTC

Agent: 我将为您执行以下操作：
- 交易对: BTC/USDT:USDT
- 方向: 买入
- 数量: 0.1 张
- 类型: 市价单

请确认是否继续？
```

### 查询订单

```
You: 查看我的未成交订单

Agent: 您有 2 个未成交订单：
1. BTC/USDT:USDT - 买入限价单 @ $44,000，数量 0.2 张
2. ETH/USDT:USDT - 卖出限价单 @ $2,400，数量 1 张
```

## 可用工具

Agent 具备以下交易工具：

1. **place_order** - 下单（市价单/限价单）
2. **cancel_order** - 取消订单
3. **query_order_status** - 查询订单状态
4. **get_open_orders** - 获取未成交订单
5. **get_positions** - 获取当前持仓
6. **get_ticker** - 获取实时行情
7. **close_position** - 平仓

## 安全提示

⚠️ **重要提示**：

1. **先在测试网测试**：设置 `HYPERLIQUID_TESTNET=true`
2. **保护 API 密钥**：不要将 `.env` 文件提交到 Git
3. **小额测试**：实盘交易前先用小额测试
4. **风险管理**：加密货币交易存在高风险
5. **谨慎操作**：Agent 会执行真实交易，请仔细确认每个操作

## 故障排除

### 网络连接问题

如果遇到依赖安装超时，可以尝试：

```bash
# 使用国内镜像
uv pip install -i https://pypi.tuna.tsinghua.edu.cn/simple ccxt langchain langgraph langchain-openai python-dotenv
```

### API 连接问题

1. 检查 API 密钥是否正确
2. 确认网络连接正常
3. 查看日志输出获取详细错误信息

### 模型调用问题

1. 确认 OpenRouter API 密钥有效
2. 检查账户余额是否充足
3. 尝试更换其他模型

## 下一步

- 查看 [API 文档](./API.md) 了解详细接口
- 阅读 [架构设计](./ARCHITECTURE.md) 了解系统设计
- 参考 [示例代码](../examples/) 学习更多用法

## 支持

如有问题，请提交 [Issue](https://github.com/aihes/Trade-Pilot/issues)

