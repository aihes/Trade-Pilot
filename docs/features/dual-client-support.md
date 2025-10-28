# Trade-Pilot 双客户端支持

## 📋 概述

Trade-Pilot 现在支持两种 Hyperliquid 客户端，您可以根据需求选择使用：

1. **CCXT 客户端** (`HyperliquidClient`) - 基于 CCXT 库
2. **官方 SDK 客户端** (`HyperliquidSDKClient`) - 基于 Hyperliquid 官方 Python SDK

## 🔄 两种客户端对比

### CCXT 客户端 (HyperliquidClient)

**优点**：
- ✅ 统一的交易所接口，易于切换到其他交易所
- ✅ 支持 100+ 个交易所
- ✅ 丰富的交易功能和工具
- ✅ 活跃的社区维护
- ✅ 完善的文档和示例

**缺点**：
- ⚠️  可能不是最新的 Hyperliquid 功能
- ⚠️  通用接口可能无法利用 Hyperliquid 特有功能

**适用场景**：
- 需要支持多个交易所的应用
- 需要统一接口的交易系统
- 已有 CCXT 经验的开发者

### 官方 SDK 客户端 (HyperliquidSDKClient)

**优点**：
- ✅ Hyperliquid 官方维护，功能最新
- ✅ 原生 API 调用，性能更好
- ✅ 支持 Hyperliquid 特有功能
- ✅ 与官方文档完全一致

**缺点**：
- ⚠️  仅支持 Hyperliquid
- ⚠️  接口与 CCXT 不同，切换交易所需要修改代码

**适用场景**：
- 专注于 Hyperliquid 的交易应用
- 需要使用 Hyperliquid 最新功能
- 追求最佳性能的应用

## 📚 使用示例

### CCXT 客户端

```python
from src.trade_pilot.hyperliquid_client import HyperliquidClient
import os
from dotenv import load_dotenv

load_dotenv()

# 初始化客户端
client = HyperliquidClient(
    wallet_address=os.getenv("WALLET_ADDRESS"),
    private_key=os.getenv("WALLET_PRIVATE_KEY"),
    testnet=False
)

# 获取价格
price = client.get_current_price("BTC/USDC:USDC")
print(f"BTC: ${price:,.2f}")

# 获取余额
balance = client.fetch_balance()

# 获取持仓
positions = client.fetch_positions(["BTC/USDC:USDC"])

# 获取 K 线数据
df = client.fetch_ohlcv("BTC/USDC:USDC", "1h", 100)
```

### 官方 SDK 客户端

```python
from src.trade_pilot.hyperliquid_sdk_client import HyperliquidSDKClient
import os
from dotenv import load_dotenv

load_dotenv()

# 初始化客户端
client = HyperliquidSDKClient(
    wallet_address=os.getenv("WALLET_ADDRESS"),
    private_key=os.getenv("WALLET_PRIVATE_KEY"),
    testnet=False
)

# 获取价格（注意：符号格式不同）
price = client.get_current_price("BTC")
print(f"BTC: ${price:,.2f}")

# 获取余额
balance = client.fetch_balance()

# 获取持仓
positions = client.fetch_positions(["BTC"])

# 获取 K 线数据
df = client.fetch_ohlcv("BTC", "1h", 100)
```

## 🔑 认证方式

两种客户端都支持相同的认证方式：

### 1. 主钱包认证

```python
# CCXT 客户端
client = HyperliquidClient(
    wallet_address="0x...",
    private_key="..."
)

# 官方 SDK 客户端
client = HyperliquidSDKClient(
    wallet_address="0x...",
    private_key="..."
)
```

### 2. API Wallet 认证

```python
# CCXT 客户端
client = HyperliquidClient(
    wallet_address="0xMainWallet",
    private_key="api_wallet_key",
    vault_address="0xSubAccount"
)

# 官方 SDK 客户端
client = HyperliquidSDKClient(
    wallet_address="0xMainWallet",
    private_key="api_wallet_key",
    vault_address="0xSubAccount"
)
```

### 3. 只读模式

```python
# CCXT 客户端
client = HyperliquidClient(read_only=True)

# 官方 SDK 客户端
client = HyperliquidSDKClient(read_only=True)
```

## 🌐 Endpoint 配置

两种客户端都支持主网、测试网和自定义 endpoint：

```python
# 主网（默认）
client = HyperliquidClient(...)
client = HyperliquidSDKClient(...)

# 测试网
client = HyperliquidClient(..., testnet=True)
client = HyperliquidSDKClient(..., testnet=True)

# 自定义 endpoint
client = HyperliquidClient(..., custom_endpoint="https://...")
client = HyperliquidSDKClient(..., custom_endpoint="https://...")
```

## 📊 主要差异

### 交易对符号格式

**CCXT 客户端**：
- 使用 CCXT 标准格式：`"BTC/USDC:USDC"`
- 包含基础货币、报价货币和结算货币

**官方 SDK 客户端**：
- 使用 Hyperliquid 原生格式：`"BTC"`
- 只需要基础货币符号

### 返回数据格式

**CCXT 客户端**：
- 返回 CCXT 标准格式的数据
- 字段名遵循 CCXT 规范

**官方 SDK 客户端**：
- 返回 Hyperliquid 原生格式的数据
- 字段名遵循 Hyperliquid API 规范

## 💡 选择建议

### 使用 CCXT 客户端，如果：
- ✅ 您计划支持多个交易所
- ✅ 您已经熟悉 CCXT
- ✅ 您需要统一的接口
- ✅ 您的应用可能迁移到其他交易所

### 使用官方 SDK 客户端，如果：
- ✅ 您只使用 Hyperliquid
- ✅ 您需要最新的 Hyperliquid 功能
- ✅ 您追求最佳性能
- ✅ 您想使用 Hyperliquid 特有功能

### 同时使用两者

您也可以在同一个项目中同时使用两种客户端：

```python
from src.trade_pilot.hyperliquid_client import HyperliquidClient
from src.trade_pilot.hyperliquid_sdk_client import HyperliquidSDKClient

# 使用 CCXT 客户端进行通用操作
ccxt_client = HyperliquidClient(...)

# 使用官方 SDK 客户端访问特有功能
sdk_client = HyperliquidSDKClient(...)
```

## 🧪 测试

### 测试 CCXT 客户端

```bash
python examples/test_hyperliquid_client.py
```

### 测试官方 SDK 客户端

```bash
python examples/test_sdk_client.py
```

### 测试认证方式

```bash
python examples/test_auth_methods.py
```

## 📖 参考文档

### CCXT 客户端
- CCXT 文档：https://docs.ccxt.com/
- CCXT Hyperliquid：https://docs.ccxt.com/#/exchanges/hyperliquid
- 客户端代码：`src/trade_pilot/hyperliquid_client.py`

### 官方 SDK 客户端
- 官方 SDK：https://github.com/hyperliquid-dex/hyperliquid-python-sdk
- Hyperliquid API 文档：https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api
- 客户端代码：`src/trade_pilot/hyperliquid_sdk_client.py`

## 🔄 迁移指南

### 从 CCXT 迁移到官方 SDK

主要需要修改的地方：

1. **导入语句**
```python
# 旧
from src.trade_pilot.hyperliquid_client import HyperliquidClient

# 新
from src.trade_pilot.hyperliquid_sdk_client import HyperliquidSDKClient
```

2. **交易对符号**
```python
# 旧
price = client.get_current_price("BTC/USDC:USDC")

# 新
price = client.get_current_price("BTC")
```

3. **其他接口基本相同**
- `fetch_balance()` - 相同
- `fetch_positions()` - 相同
- `fetch_ohlcv()` - 相同

---

**总结**：Trade-Pilot 提供了两种客户端选择，让您可以根据具体需求选择最合适的方案。无论选择哪种，都能获得完整的 Hyperliquid 交易功能支持！

