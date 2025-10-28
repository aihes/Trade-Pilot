#!/usr/bin/env python3
"""
测试 Hyperliquid 客户端的 Endpoint 配置
验证主网、测试网和自定义 endpoint 的连接
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
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_mainnet():
    """测试主网连接"""
    print_section("测试 1: 主网 (Mainnet)")
    
    try:
        # 使用只读模式测试主网
        client = HyperliquidClient(
            read_only=True,
            testnet=False
        )
        
        print(f"✅ 主网连接成功")
        print(f"   认证方式: {client.auth_method}")
        print(f"   Endpoint: https://api.hyperliquid.xyz")
        print(f"   交易对数量: {len(client.markets)}")
        
        # 测试获取价格
        btc_price = client.get_current_price("BTC/USDC:USDC")
        print(f"   BTC 价格: ${btc_price:,.2f}")
        
        return True
    except Exception as e:
        print(f"❌ 主网连接失败: {e}")
        return False


def test_testnet():
    """测试测试网连接"""
    print_section("测试 2: 测试网 (Testnet)")
    
    try:
        # 使用只读模式测试测试网
        client = HyperliquidClient(
            read_only=True,
            testnet=True
        )
        
        print(f"✅ 测试网连接成功")
        print(f"   认证方式: {client.auth_method}")
        print(f"   Endpoint: https://api.hyperliquid-testnet.xyz")
        print(f"   交易对数量: {len(client.markets)}")
        
        # 测试获取价格
        try:
            btc_price = client.get_current_price("BTC/USDC:USDC")
            print(f"   BTC 价格: ${btc_price:,.2f}")
        except Exception as e:
            print(f"   ⚠️  获取价格失败（测试网可能没有数据）: {e}")
        
        return True
    except Exception as e:
        print(f"❌ 测试网连接失败: {e}")
        return False


def test_custom_endpoint():
    """测试自定义 endpoint"""
    print_section("测试 3: 自定义 Endpoint")
    
    # 使用主网 URL 作为自定义 endpoint 示例
    custom_url = "https://api.hyperliquid.xyz"
    
    try:
        client = HyperliquidClient(
            read_only=True,
            custom_endpoint=custom_url
        )
        
        print(f"✅ 自定义 endpoint 连接成功")
        print(f"   认证方式: {client.auth_method}")
        print(f"   Endpoint: {custom_url}")
        print(f"   交易对数量: {len(client.markets)}")
        
        # 测试获取价格
        eth_price = client.get_current_price("ETH/USDC:USDC")
        print(f"   ETH 价格: ${eth_price:,.2f}")
        
        return True
    except Exception as e:
        print(f"❌ 自定义 endpoint 连接失败: {e}")
        return False


def test_wallet_with_testnet():
    """测试钱包认证 + 测试网"""
    print_section("测试 4: 钱包认证 + 测试网")
    
    wallet_address = os.getenv("WALLET_ADDRESS")
    private_key = os.getenv("WALLET_PRIVATE_KEY")
    
    if not wallet_address or not private_key:
        print("⚠️  跳过: 未配置 WALLET_ADDRESS 和 WALLET_PRIVATE_KEY")
        return None
    
    try:
        client = HyperliquidClient(
            wallet_address=wallet_address,
            private_key=private_key,
            testnet=True
        )
        
        print(f"✅ 钱包认证 + 测试网连接成功")
        print(f"   认证方式: {client.auth_method}")
        print(f"   Endpoint: https://api.hyperliquid-testnet.xyz")
        print(f"   交易对数量: {len(client.markets)}")
        
        # 测试获取余额
        try:
            balance = client.fetch_balance()
            print(f"   余额查询: ✅")
        except Exception as e:
            print(f"   ⚠️  余额查询失败: {e}")
        
        return True
    except Exception as e:
        print(f"❌ 钱包认证 + 测试网连接失败: {e}")
        return False


def test_api_with_mainnet():
    """测试 API 认证 + 主网"""
    print_section("测试 5: API 认证 + 主网")
    
    api_key = os.getenv("HYPERLIQUID_API_KEY")
    api_secret = os.getenv("HYPERLIQUID_API_SECRET")
    
    if not api_key or not api_secret:
        print("⚠️  跳过: 未配置 HYPERLIQUID_API_KEY 和 HYPERLIQUID_API_SECRET")
        return None
    
    try:
        client = HyperliquidClient(
            api_key=api_key,
            api_secret=api_secret,
            testnet=False
        )
        
        print(f"✅ API 认证 + 主网连接成功")
        print(f"   认证方式: {client.auth_method}")
        print(f"   Endpoint: https://api.hyperliquid.xyz")
        print(f"   交易对数量: {len(client.markets)}")
        
        # 测试获取价格
        sol_price = client.get_current_price("SOL/USDC:USDC")
        print(f"   SOL 价格: ${sol_price:,.2f}")
        
        return True
    except Exception as e:
        print(f"❌ API 认证 + 主网连接失败: {e}")
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 70)
    print("  Hyperliquid 客户端 Endpoint 配置测试")
    print("=" * 70)
    
    results = {}
    
    # 测试各种 endpoint 配置
    results["主网 (只读)"] = test_mainnet()
    results["测试网 (只读)"] = test_testnet()
    results["自定义 Endpoint"] = test_custom_endpoint()
    results["钱包 + 测试网"] = test_wallet_with_testnet()
    results["API + 主网"] = test_api_with_mainnet()
    
    # 总结
    print_section("测试总结")
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ 通过"
        elif result is False:
            status = "❌ 失败"
        else:
            status = "⚠️  未测试"
        print(f"  {test_name}: {status}")
    
    print("\n" + "=" * 70)
    print("  Endpoint 配置说明")
    print("=" * 70)
    print("""
1. 主网（默认）:
   client = HyperliquidClient(read_only=True)
   Endpoint: https://api.hyperliquid.xyz

2. 测试网:
   client = HyperliquidClient(read_only=True, testnet=True)
   Endpoint: https://api.hyperliquid-testnet.xyz

3. 自定义 Endpoint:
   client = HyperliquidClient(
       read_only=True,
       custom_endpoint="https://your-custom-endpoint.com"
   )

4. 钱包认证 + 测试网:
   client = HyperliquidClient(
       wallet_address="0x...",
       private_key="...",
       testnet=True
   )

5. API 认证 + 主网:
   client = HyperliquidClient(
       api_key="...",
       api_secret="...",
       testnet=False
   )
    """)
    
    print("⚠️  注意事项:")
    print("  - 测试网用于开发和测试，使用虚拟资金")
    print("  - 主网用于真实交易，使用真实资金")
    print("  - custom_endpoint 会覆盖 testnet 设置")
    print("  - 确保 endpoint URL 正确且可访问")


if __name__ == "__main__":
    main()

