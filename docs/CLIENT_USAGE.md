# Hyperliquid 客户端使用指南

## 📚 概述

Trade-Pilot 的 Hyperliquid 客户端支持三种认证方式，适用于不同的使用场景。

---

## 🔐 三种认证方式

### 1. 钱包地址 + 私钥（推荐用于交易）

**适用场景**: 需要进行交易操作（下单、取消订单等）

**优点**:
- ✅ 完全控制，无需第三方 API
- ✅ 支持所有交易功能
- ✅ 最安全的方式

**配置**:
```env
# .env 文件
WALLET_ADDRESS=0xYourWalletAddress
WALLET_PRIVATE_KEY=your_private_key
```

**使用**:
```python
from src.trade_pilot.hyperliquid_client import HyperliquidClient
import os
from dotenv import load_dotenv

load_dotenv()

client = HyperliquidClient(
    wallet_address=os.getenv("WALLET_ADDRESS"),
    private_key=os.getenv("WALLET_PRIVATE_KEY"),
    testnet=False  # True 为测试网
)

# 可以进行所有操作
balance = client.fetch_balance()
positions = client.fetch_positions(["BTC/USDC:USDC"])
order = client.place_market_order("BTC/USDC:USDC", "buy", 0.01)
```

---

### 2. API Key + Secret（官方 API 方式）

**适用场景**: 使用 Hyperliquid 官方 API

**优点**:
- ✅ 官方支持
- ✅ 可以设置权限限制
- ✅ 适合 API 集成

**配置**:
```env
# .env 文件
HYPERLIQUID_API_KEY=your_api_key
HYPERLIQUID_API_SECRET=your_api_secret
```

**使用**:
```python
client = HyperliquidClient(
    api_key=os.getenv("HYPERLIQUID_API_KEY"),
    api_secret=os.getenv("HYPERLIQUID_API_SECRET"),
    testnet=False
)

# 可以进行交易操作
ticker = client.get_ticker("ETH/USDC:USDC")
order = client.create_limit_order("ETH/USDC:USDC", "buy", 0.1, 4000)
```

---

### 3. 只读模式（无需认证）

**适用场景**: 仅查询公开数据，不进行交易

**优点**:
- ✅ 无需任何认证信息
- ✅ 最简单的使用方式
- ✅ 适合数据分析和监控

**使用**:
```python
client = HyperliquidClient(
    read_only=True,
    testnet=False
)

# 只能查询公开数据
price = client.get_current_price("BTC/USDC:USDC")
ticker = client.get_ticker("SOL/USDC:USDC")
df = client.fetch_ohlcv("BTC/USDC:USDC", "1h", 100)

# ❌ 无法进行交易操作
# order = client.place_market_order(...)  # 会失败
```

---

## 🌐 Endpoint 配置

### 主网、测试网和自定义 Endpoint

Hyperliquid 客户端支持三种 endpoint 配置：

#### 1. 主网（默认）

```python
client = HyperliquidClient(
    wallet_address=os.getenv("WALLET_ADDRESS"),
    private_key=os.getenv("WALLET_PRIVATE_KEY"),
    testnet=False  # 或者不指定，默认为 False
)
# Endpoint: https://api.hyperliquid.xyz
```

#### 2. 测试网

```python
client = HyperliquidClient(
    wallet_address=os.getenv("WALLET_ADDRESS"),
    private_key=os.getenv("WALLET_PRIVATE_KEY"),
    testnet=True  # 使用测试网
)
# Endpoint: https://api.hyperliquid-testnet.xyz
```

**测试网特点**:
- ✅ 使用虚拟资金，无真实风险
- ✅ 适合开发和测试
- ✅ 交易对数量: 1352 个（比主网多）
- ⚠️  数据可能与主网不同

#### 3. 自定义 Endpoint

```python
client = HyperliquidClient(
    wallet_address=os.getenv("WALLET_ADDRESS"),
    private_key=os.getenv("WALLET_PRIVATE_KEY"),
    custom_endpoint="https://your-custom-endpoint.com"
)
```

**注意**: `custom_endpoint` 会覆盖 `testnet` 设置

---

## 📖 常用方法

### 市场数据

```python
# 获取当前价格
price = client.get_current_price("BTC/USDC:USDC")

# 获取行情
ticker = client.get_ticker("ETH/USDC:USDC")

# 获取 K 线数据（返回 pandas DataFrame）
df = client.fetch_ohlcv(
    symbol="BTC/USDC:USDC",
    timeframe="1h",  # 1m, 5m, 15m, 30m, 1h, 4h, 12h, 1d
    limit=100
)
```

### 账户信息

```python
# 获取余额
balance = client.fetch_balance()
print(balance['total'])  # 总余额
print(balance['free'])   # 可用余额

# 获取持仓
positions = client.fetch_positions(["BTC/USDC:USDC", "ETH/USDC:USDC"])
for pos in positions:
    print(f"{pos['symbol']}: {pos['side']} {pos['contracts']}")
```

### 交易操作

```python
# 市价单
order = client.place_market_order(
    symbol="BTC/USDC:USDC",
    side="buy",  # 或 "sell"
    amount=0.01,
    reduce_only=False
)

# 市价单（带止盈止损）
order = client.place_market_order(
    symbol="BTC/USDC:USDC",
    side="buy",
    amount=0.01,
    take_profit_price=120000,  # 止盈价
    stop_loss_price=110000     # 止损价
)

# 限价单
order = client.create_limit_order(
    symbol="ETH/USDC:USDC",
    side="buy",
    amount=0.1,
    price=4000,
    reduce_only=False
)

# 取消订单
result = client.cancel_order(order_id="123", symbol="BTC/USDC:USDC")

# 查询订单
order = client.get_order(order_id="123", symbol="BTC/USDC:USDC")

# 获取未成交订单
open_orders = client.get_open_orders("BTC/USDC:USDC")
```

### 杠杆和保证金

```python
# 设置杠杆
client.set_leverage("BTC/USDC:USDC", 5)

# 设置保证金模式
client.set_margin_mode(
    symbol="BTC/USDC:USDC",
    margin_mode="isolated",  # 或 "cross"
    leverage=5
)
```

---

## 🧪 测试

### 测试所有认证方式

```bash
python examples/test_auth_methods.py
```

### 测试客户端功能

```bash
python examples/test_hyperliquid_client.py
```

---

## ⚠️ 安全注意事项

### 1. 私钥安全

```bash
# ❌ 错误：不要将私钥硬编码
client = HyperliquidClient(
    wallet_address="0x123...",
    private_key="abc123..."  # 危险！
)

# ✅ 正确：使用环境变量
client = HyperliquidClient(
    wallet_address=os.getenv("WALLET_ADDRESS"),
    private_key=os.getenv("WALLET_PRIVATE_KEY")
)
```

### 2. .env 文件

确保 `.env` 文件在 `.gitignore` 中：

```gitignore
# .gitignore
.env
.env.local
.env.*.local
```

### 3. 测试网 vs 主网

```python
# 测试网（推荐先在测试网测试）
client = HyperliquidClient(
    wallet_address=os.getenv("WALLET_ADDRESS"),
    private_key=os.getenv("WALLET_PRIVATE_KEY"),
    testnet=True  # 测试网
)

# 主网（真实资金）
client = HyperliquidClient(
    wallet_address=os.getenv("WALLET_ADDRESS"),
    private_key=os.getenv("WALLET_PRIVATE_KEY"),
    testnet=False  # 主网
)
```

---

## 🔍 错误处理

```python
try:
    client = HyperliquidClient(
        wallet_address=os.getenv("WALLET_ADDRESS"),
        private_key=os.getenv("WALLET_PRIVATE_KEY")
    )
    
    order = client.place_market_order("BTC/USDC:USDC", "buy", 0.01)
    print(f"订单成功: {order}")
    
except ValueError as e:
    print(f"配置错误: {e}")
except Exception as e:
    print(f"交易失败: {e}")
```

---

## 📊 完整示例

```python
#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from src.trade_pilot.hyperliquid_client import HyperliquidClient

# 加载环境变量
load_dotenv()

# 创建客户端
client = HyperliquidClient(
    wallet_address=os.getenv("WALLET_ADDRESS"),
    private_key=os.getenv("WALLET_PRIVATE_KEY"),
    testnet=False
)

# 1. 查询市场数据
print("=== 市场数据 ===")
btc_price = client.get_current_price("BTC/USDC:USDC")
print(f"BTC 价格: ${btc_price:,.2f}")

# 2. 查询账户信息
print("\n=== 账户信息 ===")
balance = client.fetch_balance()
print(f"USDC 余额: {balance['total'].get('USDC', 0)}")

# 3. 查询持仓
print("\n=== 持仓信息 ===")
positions = client.fetch_positions(["BTC/USDC:USDC", "ETH/USDC:USDC"])
if positions:
    for pos in positions:
        print(f"{pos['symbol']}: {pos['side']} {pos['contracts']}")
else:
    print("无持仓")

# 4. 获取 K 线数据
print("\n=== K 线数据 ===")
df = client.fetch_ohlcv("BTC/USDC:USDC", "1h", 5)
print(df)

# 5. 下单（谨慎！）
# order = client.place_market_order("BTC/USDC:USDC", "buy", 0.001)
# print(f"订单: {order}")
```

---

## 📚 相关文档

- [客户端升级报告](./HYPERLIQUID_CLIENT_UPGRADE.md)
- [测试指南](./TESTING.md)
- [CCXT 文档](https://docs.ccxt.com/)
- [Hyperliquid 文档](https://hyperliquid.gitbook.io/)

---

## 🆘 常见问题

### Q: 如何获取钱包地址和私钥？
A: 使用 MetaMask 或其他以太坊钱包，导出私钥。

### Q: API Key 在哪里获取？
A: 访问 Hyperliquid 官网，在账户设置中创建 API Key。

### Q: 只读模式可以做什么？
A: 只能查询公开数据（价格、行情、K 线等），无法进行交易。

### Q: 测试网和主网有什么区别？
A: 测试网使用虚拟资金，主网使用真实资金。建议先在测试网测试。

### Q: 如何切换测试网和主网？
A: 修改 `testnet` 参数：`testnet=True` 为测试网，`testnet=False` 为主网。

