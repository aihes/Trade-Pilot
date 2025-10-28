#!/usr/bin/env python3
"""
测试 Hyperliquid 客户端的认证方式
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.trade_pilot.hyperliquid_client import HyperliquidClient

# 加载环境变量
load_dotenv()


def print_section(title: str):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_wallet_auth():
    """测试方式 1: 主钱包认证"""
    print_section("测试 1: 主钱包认证")

    wallet_address = os.getenv("WALLET_ADDRESS")
    private_key = os.getenv("WALLET_PRIVATE_KEY")

    if not wallet_address or not private_key:
        print("⚠️  跳过: 未配置 WALLET_ADDRESS 和 WALLET_PRIVATE_KEY")
        return None

    try:
        client = HyperliquidClient(
            wallet_address=wallet_address,
            private_key=private_key,
            testnet=False
        )
        print(f"✅ 主钱包认证成功")
        print(f"   认证方式: {client.auth_method}")
        print(f"   交易对数量: {len(client.markets)}")

        # 测试获取价格
        btc_price = client.get_current_price("BTC/USDC:USDC")
        print(f"   BTC 价格: ${btc_price:,.2f}")

        # 测试获取余额
        balance = client.fetch_balance()
        print(f"   余额查询: ✅")

        return client
    except Exception as e:
        print(f"❌ 主钱包认证失败: {e}")
        return None


def test_api_wallet_auth():
    """测试方式 2: API Wallet 认证（如果配置了）"""
    print_section("测试 2: API Wallet 认证")

    wallet_address = os.getenv("WALLET_ADDRESS")
    api_wallet_key = os.getenv("API_WALLET_PRIVATE_KEY")
    vault_address = os.getenv("VAULT_ADDRESS")

    if not wallet_address or not api_wallet_key or not vault_address:
        print("⚠️  跳过: 未配置 API Wallet 相关环境变量")
        print("   需要配置: WALLET_ADDRESS, API_WALLET_PRIVATE_KEY, VAULT_ADDRESS")
        return None

    try:
        client = HyperliquidClient(
            wallet_address=wallet_address,
            private_key=api_wallet_key,
            vault_address=vault_address,
            testnet=False
        )
        print(f"✅ API Wallet 认证成功")
        print(f"   认证方式: {client.auth_method}")
        print(f"   代理账户: {vault_address[:10]}...")
        print(f"   交易对数量: {len(client.markets)}")

        # 测试获取价格
        eth_price = client.get_current_price("ETH/USDC:USDC")
        print(f"   ETH 价格: ${eth_price:,.2f}")

        return client
    except Exception as e:
        print(f"❌ API Wallet 认证失败: {e}")
        return None


def test_readonly_mode():
    """测试方式 3: 只读模式"""
    print_section("测试 3: 只读模式（无认证）")
    
    try:
        client = HyperliquidClient(
            read_only=True,
            testnet=False
        )
        print(f"✅ 只读模式初始化成功")
        print(f"   认证方式: {client.auth_method}")
        print(f"   交易对数量: {len(client.markets)}")
        
        # 测试获取价格
        sol_price = client.get_current_price("SOL/USDC:USDC")
        print(f"   SOL 价格: ${sol_price:,.2f}")
        
        # 测试获取行情
        ticker = client.get_ticker("BTC/USDC:USDC")
        print(f"   行情查询: ✅")
        
        # 测试获取 K 线
        df = client.fetch_ohlcv("BTC/USDC:USDC", "1h", 5)
        print(f"   K 线查询: ✅ ({len(df)} 根)")
        
        print("\n⚠️  注意: 只读模式无法进行交易操作")
        
        return client
    except Exception as e:
        print(f"❌ 只读模式失败: {e}")
        return None


def test_error_handling():
    """测试错误处理"""
    print_section("测试 4: 错误处理")
    
    # 测试没有提供任何认证信息
    try:
        client = HyperliquidClient()
        print("❌ 应该抛出错误但没有")
    except ValueError as e:
        print(f"✅ 正确抛出错误: {str(e)[:50]}...")
    
    # 测试只提供钱包地址没有私钥
    try:
        client = HyperliquidClient(wallet_address="0x123")
        print("❌ 应该抛出错误但没有")
    except ValueError as e:
        print(f"✅ 正确抛出错误（缺少私钥）")


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  Hyperliquid 客户端认证方式测试")
    print("=" * 60)

    # 测试认证方式
    wallet_client = test_wallet_auth()
    api_wallet_client = test_api_wallet_auth()
    readonly_client = test_readonly_mode()

    # 测试错误处理
    test_error_handling()

    # 总结
    print_section("测试总结")

    results = {
        "主钱包认证": "✅ 通过" if wallet_client else "⚠️  未测试",
        "API Wallet 认证": "✅ 通过" if api_wallet_client else "⚠️  未测试",
        "只读模式": "✅ 通过" if readonly_client else "❌ 失败",
    }

    for method, status in results.items():
        print(f"  {method}: {status}")

    print("\n推荐使用方式:")
    print("  1. 主钱包交易: wallet_address + private_key")
    print("  2. API Wallet 代理: wallet_address + api_wallet_key + vault_address")
    print("  3. 数据查询: read_only=True")

    print("\n配置示例 (.env):")
    print("  # 方式 1: 主钱包认证")
    print("  WALLET_ADDRESS=0xYourWalletAddress")
    print("  WALLET_PRIVATE_KEY=your_private_key")
    print("")
    print("  # 方式 2: API Wallet 认证（可选）")
    print("  WALLET_ADDRESS=0xYourMainWalletAddress")
    print("  API_WALLET_PRIVATE_KEY=your_api_wallet_private_key")
    print("  VAULT_ADDRESS=0xYourSubAccountOrVaultAddress")
    print("")
    print("⚠️  注意: Hyperliquid 不支持传统的 API Key + Secret 认证！")
    print("   如需使用 API Wallet，请访问 https://app.hyperliquid.xyz/API 生成")


if __name__ == "__main__":
    main()

