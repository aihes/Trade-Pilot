# Hyperliquid 认证方式说明

## 📋 研究总结

经过对 CCXT 库和 Hyperliquid 官方文档的深入研究，我们发现了一个重要事实：

**Hyperliquid 不支持传统的 API Key + Secret 认证方式！**

## 🔍 研究过程

### 1. CCXT 源码分析

查看 CCXT 对 Hyperliquid 的实现，发现其 `requiredCredentials` 配置为：

```python
{
    'apiKey': False,
    'secret': False,
    'walletAddress': True,
    'privateKey': True,
}
```

这明确表明 Hyperliquid 不使用 `apiKey` 和 `secret`，而是使用 `walletAddress` 和 `privateKey`。

### 2. GitHub Issues 研究

在 CCXT 的 GitHub Issues 中找到了关键信息（Issue #24628）：

- 用户尝试使用子账户时遇到问题
- Hyperliquid 文档说明：单个 API Wallet 为用户、vault 或子账户签名时共享同一个 nonce 集
- 如果要并行使用多个子账户，建议为每个子账户生成单独的 API Wallet

### 3. Hyperliquid 官方文档

官方文档明确说明了两种认证方式：

1. **主钱包认证**：使用主钱包的地址和私钥
2. **API Wallet 认证**：使用 API Wallet（也叫 Agent Wallet）

## ✅ 支持的认证方式

### 方式 1: 主钱包认证（推荐）

**使用场景**：个人交易，完全控制

```python
client = HyperliquidClient(
    wallet_address="0xYourWalletAddress",
    private_key="your_private_key",
    testnet=False
)
```

**优点**：
- ✅ 完全控制，无需第三方授权
- ✅ 支持所有交易功能
- ✅ 最简单直接

### 方式 2: API Wallet 认证（用于子账户/Vault）

**使用场景**：
- 代理子账户进行交易
- 代理 Vault 进行交易
- 多个子账户并行交易

```python
client = HyperliquidClient(
    wallet_address="0xMainWalletAddress",  # 主钱包地址
    private_key="api_wallet_private_key",   # API Wallet 私钥
    vault_address="0xSubAccountAddress",    # 子账户地址
    testnet=False
)
```

**如何生成 API Wallet**：
1. 访问 https://app.hyperliquid.xyz/API
2. 点击 "Generate API Wallet"
3. 保存生成的私钥
4. 授权 API Wallet 代表你的账户签名

**工作原理**：
- API Wallet 只用于签名，不用于查询账户数据
- 主账户可以批准 API Wallet 代表主账户或子账户签名
- 单个 API Wallet 为用户、vault 或子账户签名时共享同一个 nonce 集
- 如需并行使用多个子账户，建议为每个子账户生成单独的 API Wallet

### 方式 3: 只读模式

**使用场景**：仅查询公开数据，不进行交易

```python
client = HyperliquidClient(
    read_only=True,
    testnet=False
)
```

## ❌ 不支持的认证方式

### 传统 API Key + Secret

Hyperliquid **不支持**以下方式：

```python
# ❌ 这种方式不被支持！
client = HyperliquidClient(
    api_key="your_api_key",
    api_secret="your_api_secret"
)
```

**原因**：
- Hyperliquid 是基于区块链的去中心化交易所
- 所有交易都需要钱包签名
- 不使用传统的中心化交易所 API Key 机制

## 🧪 测试网使用

### 如何在测试网充值

⚠️ **重要前提**：必须先在主网用同一个钱包地址存入过资金！

**步骤**：
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

### 测试网配置

```python
client = HyperliquidClient(
    wallet_address=os.getenv("WALLET_ADDRESS"),
    private_key=os.getenv("WALLET_PRIVATE_KEY"),
    testnet=True  # 使用测试网
)
```

## 📚 代码更改

### HyperliquidClient 更新

**移除的参数**：
- `api_key`
- `api_secret`

**新增的参数**：
- `vault_address`：用于 API Wallet 代理子账户

**更新的错误提示**：
```python
raise ValueError(
    "必须提供以下认证方式之一：\n"
    "1. wallet_address + private_key（钱包认证）\n"
    "   - 主钱包模式：HyperliquidClient(wallet_address='0x...', private_key='...')\n"
    "   - API Wallet 模式：HyperliquidClient(wallet_address='0x...', private_key='...', vault_address='0x...')\n"
    "2. read_only=True（只读模式）\n"
    "\n"
    "注意：Hyperliquid 不支持传统的 API Key + Secret 认证！\n"
    "如需使用 API Wallet，请访问 https://app.hyperliquid.xyz/API 生成并授权。"
)
```

## 📖 参考文档

1. **Hyperliquid 官方文档**
   - API 文档：https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api
   - Exchange Endpoint：https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/exchange-endpoint

2. **CCXT 相关资源**
   - CCXT Hyperliquid 文档：https://docs.ccxt.com/#/exchanges/hyperliquid
   - GitHub Issue #24628：https://github.com/ccxt/ccxt/issues/24628
   - GitHub Issue #26250：https://github.com/ccxt/ccxt/issues/26250

3. **测试网资源**
   - 测试网 Faucet：https://app.hyperliquid-testnet.xyz/drip
   - API Wallet 生成：https://app.hyperliquid.xyz/API

## 🎯 最佳实践

1. **开发测试**：先在测试网测试，确认无误后再切换到主网
2. **安全性**：永远不要将私钥硬编码，使用环境变量
3. **子账户管理**：如需并行使用多个子账户，为每个子账户生成单独的 API Wallet
4. **错误处理**：始终使用 try-except 捕获异常

## 📝 更新日志

**2025-01-28**：
- 移除 API Key + Secret 认证支持
- 添加 API Wallet（vault_address）支持
- 更新文档和测试脚本
- 添加测试网充值说明
- 澄清 Hyperliquid 认证机制

---

**总结**：Hyperliquid 作为去中心化交易所，使用基于钱包的认证方式，而非传统的 API Key + Secret。这是其去中心化特性的体现，所有交易都需要钱包签名来确保安全性。

