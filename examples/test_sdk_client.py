#!/usr/bin/env python3
"""
测试 Hyperliquid 官方 SDK 客户端
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.trade_pilot.hyperliquid_sdk_client import HyperliquidSDKClient

# 加载环境变量
load_dotenv()


def print_section(title: str):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_sdk_client():
    """测试官方 SDK 客户端"""
    print_section("测试 Hyperliquid 官方 SDK 客户端")
    
    wallet_address = os.getenv("WALLET_ADDRESS")
    private_key = os.getenv("WALLET_PRIVATE_KEY")
    
    if not wallet_address or not private_key:
        print("⚠️  未配置 WALLET_ADDRESS 和 WALLET_PRIVATE_KEY")
        print("   使用只读模式测试...")
        
        # 只读模式测试
        client = HyperliquidSDKClient(read_only=True, testnet=False)
    else:
        # 钱包认证模式
        client = HyperliquidSDKClient(
            wallet_address=wallet_address,
            private_key=private_key,
            testnet=False
        )
    
    print(f"✅ 客户端初始化成功")
    print(f"   认证方式: {client.auth_method}")
    print(f"   API URL: {client.api_url}")
    print(f"   交易对数量: {len(client.markets)}")
    
    # 测试获取价格
    print_section("测试获取价格")
    try:
        btc_price = client.get_current_price("BTC")
        print(f"✅ BTC 价格: ${btc_price:,.2f}")
        
        eth_price = client.get_current_price("ETH")
        print(f"✅ ETH 价格: ${eth_price:,.2f}")
        
        sol_price = client.get_current_price("SOL")
        print(f"✅ SOL 价格: ${sol_price:,.2f}")
    except Exception as e:
        print(f"❌ 获取价格失败: {e}")
    
    # 测试获取行情
    print_section("测试获取行情")
    try:
        ticker = client.get_ticker("BTC")
        print(f"✅ BTC 行情:")
        print(f"   Last: ${ticker['last']:,.2f}")
        print(f"   Bid: ${ticker['bid']:,.2f}")
        print(f"   Ask: ${ticker['ask']:,.2f}")
    except Exception as e:
        print(f"❌ 获取行情失败: {e}")
    
    # 测试获取 K 线数据
    print_section("测试获取 K 线数据")
    try:
        df = client.fetch_ohlcv("BTC", "1h", 5)
        print(f"✅ 获取 K 线数据成功:")
        print(f"   数据行数: {len(df)}")
        print(f"   列: {list(df.columns)}")
        print(f"\n最新 K 线:")
        if len(df) > 0:
            latest = df.iloc[-1]
            print(f"   Open: ${latest['open']:,.2f}")
            print(f"   High: ${latest['high']:,.2f}")
            print(f"   Low: ${latest['low']:,.2f}")
            print(f"   Close: ${latest['close']:,.2f}")
            print(f"   Volume: {latest['volume']:,.2f}")
    except Exception as e:
        print(f"❌ 获取 K 线数据失败: {e}")
    
    # 如果不是只读模式，测试获取余额和持仓
    if not client.read_only:
        print_section("测试获取余额")
        try:
            balance = client.fetch_balance()
            print(f"✅ 获取余额成功:")
            if 'total' in balance and 'USDC' in balance['total']:
                print(f"   总余额: ${balance['total']['USDC']:,.2f} USDC")
            else:
                print(f"   余额信息: {balance}")
        except Exception as e:
            print(f"❌ 获取余额失败: {e}")
        
        print_section("测试获取持仓")
        try:
            positions = client.fetch_positions()
            print(f"✅ 获取持仓成功:")
            print(f"   持仓数量: {len(positions)}")
            
            if positions:
                for pos in positions:
                    print(f"\n   {pos['symbol']}:")
                    print(f"     方向: {pos['side']}")
                    print(f"     数量: {pos['size']}")
                    print(f"     入场价: ${pos['entry_price']:,.2f}")
                    print(f"     未实现盈亏: ${pos['unrealized_pnl']:,.2f}")
                    print(f"     杠杆: {pos['leverage']}x")
            else:
                print("   无持仓")
        except Exception as e:
            print(f"❌ 获取持仓失败: {e}")
    
    print_section("测试总结")
    print(f"✅ 官方 SDK 客户端测试完成！")
    print(f"\n客户端信息:")
    print(f"  {client}")


def test_comparison():
    """对比 CCXT 客户端和官方 SDK 客户端"""
    print_section("对比两种客户端")
    
    print("\n📊 CCXT 客户端 vs 官方 SDK 客户端\n")
    
    print("CCXT 客户端 (HyperliquidClient):")
    print("  ✅ 统一的交易所接口")
    print("  ✅ 支持多个交易所")
    print("  ✅ 丰富的交易功能")
    print("  ✅ 社区维护")
    print("  ⚠️  可能不是最新的 Hyperliquid 功能")
    
    print("\n官方 SDK 客户端 (HyperliquidSDKClient):")
    print("  ✅ Hyperliquid 官方维护")
    print("  ✅ 最新的功能支持")
    print("  ✅ 原生 API 调用")
    print("  ✅ 更好的性能")
    print("  ⚠️  仅支持 Hyperliquid")
    
    print("\n💡 建议:")
    print("  - 如果只交易 Hyperliquid: 使用官方 SDK 客户端")
    print("  - 如果需要多交易所支持: 使用 CCXT 客户端")
    print("  - 可以同时使用两者，根据需求选择")


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("  Hyperliquid 官方 SDK 客户端测试")
    print("=" * 60)
    
    # 测试官方 SDK 客户端
    test_sdk_client()
    
    # 对比两种客户端
    test_comparison()
    
    print("\n" + "=" * 60)
    print("  测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

