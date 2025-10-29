# Trade-Pilot 示例代码使用指南

## 📋 概述

本指南介绍如何运行 Trade-Pilot 项目中的所有示例代码。所有示例都已经过测试，可以正常运行。

## 🔧 前置准备

### 1. 环境配置

确保 `.env` 文件中配置了以下必要的环境变量：

```bash
# Hyperliquid API Wallet 配置（官方推荐方式）
# API Wallet 地址（从 https://app.hyperliquid.xyz/API 生成）
HYPERLIQUID_API_KEY=0xYourAPIWalletAddress
# API Wallet 私钥（用于签名交易）
HYPERLIQUID_API_SECRET=your_api_wallet_private_key

# 主钱包地址（用于查询账户数据，可选）
# 如果 API Wallet 代理主账户，则与 API Key 相同
# 如果 API Wallet 代理子账户，这里填主账户地址
WALLET_ADDRESS=0xYourMainWalletAddress

# Vault 地址（可选，仅当 API Wallet 代理子账户/Vault 时需要）
# VAULT_ADDRESS=0xYourVaultAddress

# Hyperliquid 网络配置
HYPERLIQUID_TESTNET=true  # true=测试网, false=主网

# OpenRouter API 配置（用于 AI Agent）
OPENROUTER_API_KEY=sk-or-v1-your_api_key

# 模型配置
MODEL_NAME=anthropic/claude-3.5-sonnet
```

### 2. 安装依赖

```bash
uv sync
```

## 📚 示例文件说明

### 1. `basic_usage.py` - 基础使用示例

**功能**：演示 Trade-Pilot 的基本功能，包括查询价格、余额、持仓等。

**运行方式**：
```bash
python examples/basic_usage.py
```

**交互选项**：
- `1` - 基础交易示例（查询价格、余额、持仓）
- `2` - Agent 交易示例（使用 AI Agent 进行查询）
- `3` - 交互式聊天（与 AI Agent 对话）

**示例输出**：
```
✅ 使用钱包认证模式
   钱包地址: 0xfedb4cD941E875614e9D9347FDf421e005b27E42
   网络: 测试网

=== 账户余额 ===
  USDC: 0.00

=== BTC 行情 ===
  当前价格: $115,669.50

=== 当前持仓 ===
  无持仓

=== 未成交订单 ===
  无未成交订单
```

**需要的环境变量**：
- `HYPERLIQUID_API_KEY` - API Wallet 地址
- `HYPERLIQUID_API_SECRET` - API Wallet 私钥
- `WALLET_ADDRESS` - 主钱包地址（可选）
- `HYPERLIQUID_TESTNET` - 网络选择
- `OPENROUTER_API_KEY` - OpenRouter API Key（仅 Agent 功能需要）

---

### 2. `test_hyperliquid_client.py` - CCXT 客户端测试

**功能**：全面测试 CCXT 客户端的所有功能。

**运行方式**：
```bash
python examples/test_hyperliquid_client.py
```

**测试内容**：
- ✅ 客户端初始化
- ✅ 获取账户余额
- ✅ 获取当前价格
- ✅ 获取持仓信息
- ✅ 获取 K 线数据
- ✅ 下单功能（需要确认）
- ✅ 取消订单
- ✅ 查询订单状态

**示例输出**：
```
============================================================
  测试 1: 客户端初始化
============================================================
✅ 客户端初始化成功
✅ 加载了 450 个交易对

============================================================
  测试 3: 获取当前价格
============================================================
✅ BTC/USDC:USDC: $112,495.50
✅ ETH/USDC:USDC: $3,978.15
✅ SOL/USDC:USDC: $194.29
```

**需要的环境变量**：
- `HYPERLIQUID_API_KEY`
- `HYPERLIQUID_API_SECRET`
- `WALLET_ADDRESS`（可选）
- `HYPERLIQUID_TESTNET`

---

### 3. `test_sdk_client.py` - 官方 SDK 客户端测试

**功能**：测试 Hyperliquid 官方 SDK 客户端的功能。

**运行方式**：
```bash
python examples/test_sdk_client.py
```

**测试内容**：
- ✅ 客户端初始化
- ✅ 获取价格
- ✅ 获取行情
- ✅ 获取 K 线数据
- ✅ 获取余额
- ✅ 获取持仓
- ✅ 两种客户端对比

**示例输出**：
```
============================================================
  测试 Hyperliquid 官方 SDK 客户端
============================================================
✅ 客户端初始化成功
   认证方式: main_wallet
   API URL: https://api.hyperliquid.xyz
   交易对数量: 218

============================================================
  测试获取价格
============================================================
✅ BTC 价格: $112,494.50
✅ ETH 价格: $3,977.75
✅ SOL 价格: $194.25
```

**需要的环境变量**：
- `HYPERLIQUID_API_KEY`
- `HYPERLIQUID_API_SECRET`
- `WALLET_ADDRESS`（可选）
- `HYPERLIQUID_TESTNET`

---

### 4. `test_auth_methods.py` - 认证方式测试

**功能**：测试所有支持的认证方式。

**运行方式**：
```bash
python examples/test_auth_methods.py
```

**测试内容**：
- ✅ 主钱包认证
- ✅ API Wallet 认证（如果配置）
- ✅ 只读模式
- ✅ 错误处理

**示例输出**：
```
============================================================
  测试 1: 主钱包认证
============================================================
✅ 主钱包认证成功
   认证方式: wallet
   交易对数量: 450
   BTC 价格: $112,473.50
   余额查询: ✅

============================================================
  测试 3: 只读模式（无认证）
============================================================
✅ 只读模式初始化成功
   认证方式: read_only
   交易对数量: 450
   SOL 价格: $194.21
```

**需要的环境变量**：
- `HYPERLIQUID_API_KEY` - API Wallet 地址
- `HYPERLIQUID_API_SECRET` - API Wallet 私钥
- `WALLET_ADDRESS` - 主钱包地址（可选）
- `VAULT_ADDRESS` - 子账户测试（可选）
- `HYPERLIQUID_TESTNET` - 网络选择

---

### 5. `test_endpoints.py` - Endpoint 配置测试

**功能**：测试主网、测试网和自定义 endpoint 配置。

**运行方式**：
```bash
python examples/test_endpoints.py
```

**测试内容**：
- ✅ 主网连接
- ✅ 测试网连接
- ✅ 自定义 endpoint
- ✅ 钱包认证 + 测试网
- ✅ Endpoint 配置说明

**示例输出**：
```
============================================================
  测试 1: 主网 (Mainnet)
============================================================
✅ 主网连接成功
   Endpoint: https://api.hyperliquid.xyz
   交易对数量: 450
   BTC 价格: $112,503.50

============================================================
  测试 2: 测试网 (Testnet)
============================================================
✅ 测试网连接成功
   Endpoint: https://api.hyperliquid-testnet.xyz
   交易对数量: 1352
   BTC 价格: $115,669.50
```

**需要的环境变量**：
- `HYPERLIQUID_API_KEY` - API Wallet 认证测试（可选）
- `HYPERLIQUID_API_SECRET` - API Wallet 认证测试（可选）
- `WALLET_ADDRESS` - 主钱包地址（可选）

---

### 6. `test_agent.py` - AI Agent 测试

**功能**：测试 AI Agent 的对话和交易功能（使用 Mock 客户端）。

**运行方式**：
```bash
# 运行预设测试
python examples/test_agent.py

# 启动交互式聊天
python examples/test_agent.py --chat
```

**测试内容**：
- ✅ Agent 初始化
- ✅ 查询 BTC 价格
- ✅ 查询持仓
- ✅ 查询账户余额
- ✅ 交互式聊天（可选）

**示例输出**：
```
============================================================
测试 1: 查询 BTC 价格
============================================================

用户: 帮我查看 BTC 的当前价格
Agent: 根据实时行情数据，BTC 的当前情况如下：
- 最新成交价：1009.36 USDC
- 买一价：1009.26 USDC
- 卖一价：1009.46 USDC
```

**需要的环境变量**：
- `OPENROUTER_API_KEY` - OpenRouter API Key

---

## 🚀 快速开始

### 最简单的测试（无需钱包）

如果你还没有配置钱包，可以先运行只读模式的测试：

```bash
# 测试 endpoint 配置（只读模式）
python examples/test_endpoints.py

# 测试 AI Agent（使用 Mock 客户端）
python examples/test_agent.py
```

### 完整功能测试（需要钱包）

配置好 `.env` 文件后，运行完整测试：

```bash
# 1. 测试 CCXT 客户端
python examples/test_hyperliquid_client.py

# 2. 测试官方 SDK 客户端
python examples/test_sdk_client.py

# 3. 测试认证方式
python examples/test_auth_methods.py

# 4. 运行基础示例
echo "1" | python examples/basic_usage.py
```

## ⚠️ 注意事项

### 1. 测试网 vs 主网

- **测试网**：使用虚拟资金，适合开发和测试
  - 设置 `HYPERLIQUID_TESTNET=true`
  - 需要先在主网存入资金才能使用测试网 faucet
  - Faucet: https://app.hyperliquid-testnet.xyz/drip

- **主网**：使用真实资金，请谨慎操作
  - 设置 `HYPERLIQUID_TESTNET=false`
  - 确保充分测试后再使用

### 2. 认证方式

Hyperliquid **不支持**传统的 API Key + Secret 认证！

支持的认证方式：
1. **主钱包认证**：`WALLET_ADDRESS` + `WALLET_PRIVATE_KEY`
2. **API Wallet 认证**：`WALLET_ADDRESS` + `API_WALLET_PRIVATE_KEY` + `VAULT_ADDRESS`
3. **只读模式**：无需认证，只能查询数据

### 3. 安全建议

- ✅ 不要在代码中硬编码私钥
- ✅ 使用 `.env` 文件管理敏感信息
- ✅ 不要将 `.env` 文件提交到 Git
- ✅ 先在测试网测试，确认无误后再使用主网
- ✅ 使用 API Wallet 而不是主钱包私钥（更安全）

## 📖 相关文档

- [客户端使用指南](CLIENT_USAGE.md)
- [双客户端支持](features/dual-client-support.md)
- [认证方式研究](features/hyperliquid-authentication.md)
- [Hyperliquid 官方文档](https://hyperliquid.gitbook.io/hyperliquid-docs/)

## 🐛 故障排除

### 问题 1: 连接失败

```
错误: 请在 .env 文件中设置 WALLET_ADDRESS 和 WALLET_PRIVATE_KEY
```

**解决方案**：检查 `.env` 文件是否正确配置了钱包地址和私钥。

### 问题 2: 测试网余额为 0

**解决方案**：
1. 确保你的钱包地址在主网有过存款记录
2. 访问测试网 faucet: https://app.hyperliquid-testnet.xyz/drip
3. 领取测试 USDC

### 问题 3: Agent 无法运行

```
错误: 请在 .env 文件中设置 OPENROUTER_API_KEY
```

**解决方案**：在 `.env` 文件中配置 OpenRouter API Key。

---

**祝你使用愉快！** 🎉

