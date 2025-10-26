# Trade-Pilot 测试指南

## 快速测试

项目已经配置好并可以运行！使用 Mock 客户端进行测试，无需真实的 Hyperliquid API 密钥。

### 1. 运行自动化测试

```bash
python examples/test_agent.py
```

这将运行 3 个测试用例：
- ✅ 查询 BTC 价格
- ✅ 查询持仓
- ✅ 查询账户余额

### 2. 启动交互式聊天

```bash
python examples/test_agent.py --chat
```

然后你可以与 Agent 进行对话：

```
You: 帮我查看 BTC 的当前价格

Agent: 根据实时行情数据：
- 当前 BTC 最新成交价格：44,824.42 USDT
- 买一价（bid）：44,819.94 USDT
...
```

## 测试功能

### 可用命令示例

1. **查询行情**
   ```
   帮我查看 BTC 的当前价格
   查看 ETH 的行情
   ```

2. **查询持仓**
   ```
   我现在有哪些持仓？
   查看我的持仓情况
   ```

3. **查询余额**
   ```
   查看我的账户余额
   我有多少钱？
   ```

4. **查询订单**
   ```
   查看我的未成交订单
   有哪些挂单？
   ```

5. **下单（Mock 模式）**
   ```
   帮我以市价买入 0.1 张 BTC
   在 44000 美元挂一个买入限价单，数量 0.2 张 BTC
   ```

## Mock 数据说明

Mock 客户端提供以下模拟数据：

### 账户余额
```json
{
  "total": {
    "USDT": 10000.0,
    "BTC": 0.5,
    "ETH": 2.0
  }
}
```

### 持仓
```json
[
  {
    "symbol": "BTC/USDT:USDT",
    "side": "long",
    "contracts": 0.1,
    "entryPrice": 44000.0,
    "markPrice": 45000.0,
    "unrealizedPnl": 100.0
  },
  {
    "symbol": "ETH/USDT:USDT",
    "side": "short",
    "contracts": 1.0,
    "entryPrice": 2400.0,
    "markPrice": 2300.0,
    "unrealizedPnl": 100.0
  }
]
```

### 价格（随机波动）
- BTC/USDT:USDT: ~45000 USDT
- ETH/USDT:USDT: ~2300 USDT
- SOL/USDT:USDT: ~100 USDT

## 环境配置

确保 `.env` 文件中配置了 OpenRouter API Key：

```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
MODEL_NAME=anthropic/claude-3.5-sonnet
```

## 切换到真实交易

要使用真实的 Hyperliquid API：

1. 修改测试脚本，使用 `HyperliquidClient` 而不是 `MockHyperliquidClient`：

```python
from src.trade_pilot import HyperliquidClient, TradingAgent

# 创建真实客户端
client = HyperliquidClient(
    api_key=os.getenv("HYPERLIQUID_API_KEY"),
    api_secret=os.getenv("HYPERLIQUID_API_SECRET"),
    testnet=True  # 先在测试网测试
)
```

2. 在 `.env` 中配置 Hyperliquid API 密钥：

```env
HYPERLIQUID_API_KEY=your_api_key_here
HYPERLIQUID_API_SECRET=your_api_secret_here
HYPERLIQUID_TESTNET=true
```

## 调试提示词

Agent 的系统提示词在 `src/trade_pilot/agent.py` 的 `run()` 方法中定义。

你可以修改提示词来调整 Agent 的行为：

```python
system_prompt = """你是一个专业的加密货币交易助手。
你可以帮助用户在 Hyperliquid 平台上执行交易操作。

你有以下能力：
1. 下单（市价单和限价单）
2. 取消订单
3. 查询订单状态
...

在执行交易操作前，请务必：
- 确认用户的交易意图
- 检查当前市场行情
- 评估风险
- 向用户说明操作的影响
"""
```

## 常见问题

### Q: Agent 返回 401 错误
A: 检查 `OPENROUTER_API_KEY` 是否正确配置在 `.env` 文件中。

### Q: 如何查看详细日志？
A: 在 `.env` 中设置 `LOG_LEVEL=DEBUG`

### Q: Mock 数据可以自定义吗？
A: 可以！编辑 `src/trade_pilot/mock_client.py` 中的数据。

### Q: 如何添加新的交易工具？
A: 在 `src/trade_pilot/tools.py` 中添加新的工具类，并在 `create_trading_tools()` 中注册。

## 下一步

1. ✅ 测试基础功能
2. 🔲 调整提示词优化 Agent 行为
3. 🔲 集成 Jina AI 进行新闻搜索
4. 🔲 添加技术指标分析
5. 🔲 开发交易策略
6. 🔲 在测试网进行真实交易测试

## 技术栈

- **LangChain**: AI 应用框架
- **LangGraph**: Agent 工作流编排
- **OpenRouter**: AI 模型接入
- **CCXT**: 交易所 API 封装
- **Hyperliquid**: 去中心化永续合约交易所

## 支持

如有问题，请查看：
- [项目总结](./PROJECT_SUMMARY.md)
- [快速开始](./QUICKSTART.md)
- [GitHub Issues](https://github.com/aihes/Trade-Pilot/issues)

