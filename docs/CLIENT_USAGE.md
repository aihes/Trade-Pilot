# Hyperliquid 客户端使用指南

## 📚 概述

Trade-Pilot 的 Hyperliquid 客户端支持两种认证方式，适用于不同的使用场景。

**重要提示**：Hyperliquid **不支持**传统的 API Key + Secret 认证方式！如需使用 API Wallet，请参考下方的 API Wallet 使用说明。

---

## 🔐 两种认证方式

### 1. 钱包地址 + 私钥（推荐用于交易）

**适用场景**: 需要进行交易操作（下单、取消订单等）

**优点**:
- ✅ 完全控制，无需第三方 API
- ✅ 支持所有交易功能
- ✅ 最安全的方式

#### 1.1 主钱包模式（最常用）

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

# 主钱包认证
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

#### 1.2 API Wallet 模式（用于子账户/Vault）

**什么是 API Wallet？**
- API Wallet（也叫 Agent Wallet）是一种特殊的钱包
- 需要通过主账户在 https://app.hyperliquid.xyz/API 生成并授权
- 可以代表主账户、子账户或 Vault 进行签名
- 只用于签名，不用于查询账户数据

**使用场景**:
- 代理子账户进行交易
- 代理 Vault 进行交易
- 多个子账户并行交易（每个子账户使用不同的 API Wallet）

**配置**:
```env
# .env 文件
WALLET_ADDRESS=0xYourMainWalletAddress  # 主钱包地址
API_WALLET_PRIVATE_KEY=your_api_wallet_private_key  # API Wallet 私钥
VAULT_ADDRESS=0xYourSubAccountOrVaultAddress  # 子账户或 Vault 地址
```

**使用**:
```python
# API Wallet 认证（代理子账户）
client = HyperliquidClient(
    wallet_address=os.getenv("WALLET_ADDRESS"),  # 主钱包地址
    private_key=os.getenv("API_WALLET_PRIVATE_KEY"),  # API Wallet 私钥
    vault_address=os.getenv("VAULT_ADDRESS"),  # 子账户地址
    testnet=False
)

# 所有交易操作都会在子账户上执行
order = client.place_market_order("BTC/USDC:USDC", "buy", 0.01)
```

**如何生成 API Wallet？**
1. 访问 https://app.hyperliquid.xyz/API
2. 点击 "Generate API Wallet"
3. 保存生成的私钥（API_WALLET_PRIVATE_KEY）
4. 授权 API Wallet 代表你的主账户或子账户签名

---

### 2. 只读模式（无需认证）

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

**如何在测试网充值？**

⚠️ **重要前提**：必须先在主网用同一个钱包地址存入过资金！

1. 在主网用你的钱包地址存入过资金（任意金额）
2. 访问测试网 faucet：https://app.hyperliquid-testnet.xyz/drip
3. 连接你的钱包
4. 点击 "Claim" 领取测试币
5. 每次可领取 1,000 mock USDC

**如果使用邮箱登录**：
- Privy 会为主网和测试网生成不同的钱包地址
- 需要从主网导出钱包私钥
- 导入到 Metamask 或 Rabby 钱包
- 然后连接到测试网

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

### Q: Hyperliquid 支持 API Key + Secret 认证吗？

A: **不支持！** Hyperliquid 不使用传统的 API Key + Secret 认证方式。如果你需要使用 API 进行自动化交易，有两种方式：
1. 直接使用主钱包的地址和私钥
2. 生成 API Wallet（Agent Wallet）并使用其私钥

### Q: 什么是 API Wallet？如何生成？

A: API Wallet（也叫 Agent Wallet）是一种特殊的钱包，用于代表主账户或子账户进行签名。

**生成步骤**：
1. 访问 https://app.hyperliquid.xyz/API
2. 点击 "Generate API Wallet"
3. 保存生成的私钥
4. 授权 API Wallet 代表你的账户签名

### Q: 只读模式可以做什么？

A: 只能查询公开数据（价格、行情、K 线等），无法进行交易。

### Q: 测试网和主网有什么区别？

A: 测试网使用虚拟资金，主网使用真实资金。建议先在测试网测试。

### Q: 如何在测试网充值？

A:
1. **前提**：必须先在主网用同一地址存入过资金
2. 访问 https://app.hyperliquid-testnet.xyz/drip
3. 连接钱包并领取测试币（每次 1,000 mock USDC）

### Q: 如何切换测试网和主网？

A: 修改 `testnet` 参数：`testnet=True` 为测试网，`testnet=False` 为主网。

### Q: 如何使用 API Wallet 代理子账户交易？

A: 使用 `vault_address` 参数：

```python
client = HyperliquidClient(
    wallet_address="0xMainWallet",  # 主钱包地址
    private_key="api_wallet_private_key",  # API Wallet 私钥
    vault_address="0xSubAccount"  # 子账户地址
)
```

