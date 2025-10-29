# Hyperliquid 永续合约交易功能

## 📋 概述

Trade-Pilot 通过 Hyperliquid 官方 SDK 提供完整的永续合约交易功能支持。

## 🔑 支持的功能

### 1. 基础功能

#### 获取价格和行情
```python
from trade_pilot import HyperliquidSDKClient

client = HyperliquidSDKClient(
    wallet_address="0x...",
    private_key="...",
    testnet=True
)

# 获取当前价格
btc_price = client.get_current_price("BTC")
print(f"BTC 价格: ${btc_price:,.2f}")

# 获取详细行情
ticker = client.get_ticker("BTC")
print(f"买一价: ${ticker['bid']}")
print(f"卖一价: ${ticker['ask']}")
```

#### 查询账户信息
```python
# 获取余额
balance = client.fetch_balance()
total = balance['total']['USDC']
free = balance['free']['USDC']

# 获取持仓
positions = client.fetch_positions()
for pos in positions:
    print(f"{pos['symbol']}: {pos['side']} {pos['size']} @ ${pos['entry_price']}")

# 获取未成交订单
orders = client.get_open_orders()
for order in orders:
    print(f"{order['symbol']}: {order['side']} {order['amount']} @ ${order['price']}")
```

### 2. 订单管理

#### 下限价单
```python
from hyperliquid.utils.signing import OrderType

# 买入限价单
result = client.exchange.order(
    name="BTC",           # 交易对
    is_buy=True,          # True=买入, False=卖出
    sz=0.001,             # 数量
    limit_px=100000.0,    # 限价
    order_type=OrderType.LIMIT,
    reduce_only=False     # False=开仓, True=只减仓
)

# 卖出限价单
result = client.exchange.order(
    name="BTC",
    is_buy=False,
    sz=0.001,
    limit_px=120000.0,
    order_type=OrderType.LIMIT,
    reduce_only=False
)
```

#### 查询订单
```python
# 查询所有未成交订单
all_orders = client.get_open_orders()

# 查询特定交易对的订单
btc_orders = client.get_open_orders("BTC")

# 订单信息包含:
# - id: 订单ID
# - symbol: 交易对
# - side: 方向 (buy/sell)
# - type: 类型
# - price: 价格
# - amount: 数量
# - filled: 已成交数量
# - remaining: 剩余数量
# - timestamp: 时间戳
```

#### 取消订单
```python
# 取消单个订单
result = client.exchange.cancel(
    name="BTC",
    oid=12345  # 订单ID
)

# 批量取消订单
from hyperliquid.utils.signing import CancelRequest

cancel_requests = [
    CancelRequest(coin="BTC", oid=12345),
    CancelRequest(coin="ETH", oid=67890),
]
result = client.exchange.bulk_cancel(cancel_requests)
```

#### 修改订单
```python
# 修改订单价格和数量
result = client.exchange.modify_order(
    oid=12345,            # 订单ID
    name="BTC",
    is_buy=True,
    sz=0.002,             # 新数量
    limit_px=105000.0,    # 新价格
    order_type=OrderType.LIMIT,
    reduce_only=False
)
```

### 3. 市价单

#### 市价开仓
```python
# 市价买入（做多）
result = client.exchange.market_open(
    name="BTC",
    is_buy=True,
    sz=0.001,
    px=115000.0,      # 参考价格（用于计算滑点）
    slippage=0.05     # 5% 滑点容忍度
)

# 市价卖出（做空）
result = client.exchange.market_open(
    name="BTC",
    is_buy=False,
    sz=0.001,
    px=115000.0,
    slippage=0.05
)
```

#### 市价平仓
```python
# 平仓全部持仓
result = client.exchange.market_close(
    coin="BTC",
    slippage=0.05
)

# 平仓部分持仓
result = client.exchange.market_close(
    coin="BTC",
    sz=0.001,         # 平仓数量
    px=115000.0,      # 参考价格
    slippage=0.05
)
```

### 4. 杠杆管理

#### 修改杠杆
```python
# 设置全仓杠杆
result = client.exchange.update_leverage(
    leverage=5,       # 杠杆倍数 (1-50)
    name="BTC",
    is_cross=True     # True=全仓, False=逐仓
)

# 设置逐仓杠杆
result = client.exchange.update_leverage(
    leverage=10,
    name="BTC",
    is_cross=False
)
```

#### 修改逐仓保证金
```python
# 增加保证金
result = client.exchange.update_isolated_margin(
    amount=100.0,     # 增加 100 USDC
    name="BTC"
)

# 减少保证金（使用负数）
result = client.exchange.update_isolated_margin(
    amount=-50.0,     # 减少 50 USDC
    name="BTC"
)
```

### 5. 批量操作

#### 批量下单
```python
from hyperliquid.utils.signing import OrderRequest

order_requests = [
    OrderRequest(
        coin="BTC",
        is_buy=True,
        sz=0.001,
        limit_px=100000.0,
        order_type=OrderType.LIMIT,
        reduce_only=False
    ),
    OrderRequest(
        coin="ETH",
        is_buy=True,
        sz=0.01,
        limit_px=3500.0,
        order_type=OrderType.LIMIT,
        reduce_only=False
    ),
]

result = client.exchange.bulk_orders(order_requests)
```

## 🧪 测试网使用

### 1. 获取测试网资金

**前提条件**：需要先在主网存入过资金（同一个钱包地址）

**步骤**：
1. 访问测试网 Faucet: https://app.hyperliquid-testnet.xyz/drip
2. 连接你的钱包
3. 领取 1,000 mock USDC

### 2. 运行测试脚本

```bash
# 确保 .env 配置正确
HYPERLIQUID_API_KEY=0x...
HYPERLIQUID_API_SECRET=0x...
HYPERLIQUID_TESTNET=true

# 运行永续合约测试
python examples/test_perp_trading.py
```

## ⚠️ 重要提示

### 风险警告

1. **市价单风险**：市价单会立即成交，可能产生滑点
2. **杠杆风险**：高杠杆会放大盈亏，可能导致爆仓
3. **测试网限制**：测试网数据仅供测试，不代表主网表现

### 最佳实践

1. **先在测试网测试**：所有策略都应该先在测试网充分测试
2. **使用限价单**：限价单可以控制成交价格，避免滑点
3. **设置止损**：使用 `reduce_only=True` 设置止损单
4. **小额测试**：从小额开始，逐步增加交易量
5. **监控持仓**：定期检查持仓和未成交订单

## 📖 完整示例

查看 `examples/test_perp_trading.py` 获取完整的测试示例。

## 🔗 参考文档

- Hyperliquid 官方文档: https://hyperliquid.gitbook.io/hyperliquid-docs
- Hyperliquid Python SDK: https://github.com/hyperliquid-dex/hyperliquid-python-sdk
- API 文档: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api

