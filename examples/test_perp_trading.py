#!/usr/bin/env python3
"""
测试 Hyperliquid 永续合约交易功能
使用官方 SDK 进行完整的交易流程测试
"""

import os
import sys
import time
from dotenv import load_dotenv

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.trade_pilot.hyperliquid_sdk_client import HyperliquidSDKClient

# 加载环境变量
load_dotenv()


def print_section(title: str):
    """打印分隔线"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_get_current_price(client: HyperliquidSDKClient):
    """测试 1: 获取当前价格"""
    print_section("测试 1: 获取当前价格")
    
    try:
        btc_price = client.get_current_price("BTC")
        eth_price = client.get_current_price("ETH")
        sol_price = client.get_current_price("SOL")
        
        print(f"✅ BTC 价格: ${btc_price:,.2f}")
        print(f"✅ ETH 价格: ${eth_price:,.2f}")
        print(f"✅ SOL 价格: ${sol_price:,.2f}")
        
        return btc_price
    except Exception as e:
        print(f"❌ 获取价格失败: {e}")
        return None


def test_get_account_info(client: HyperliquidSDKClient):
    """测试 2: 获取账户信息"""
    print_section("测试 2: 获取账户信息")
    
    try:
        # 获取余额
        balance = client.fetch_balance()
        total_balance = balance.get('total', {}).get('USDC', 0)
        free_balance = balance.get('free', {}).get('USDC', 0)
        
        print(f"✅ 账户余额:")
        print(f"   总余额: ${total_balance:,.2f} USDC")
        print(f"   可用余额: ${free_balance:,.2f} USDC")
        
        # 获取持仓
        positions = client.fetch_positions()
        print(f"\n✅ 当前持仓: {len(positions)} 个")
        for pos in positions:
            print(f"   {pos['symbol']}: {pos['side']} {pos['size']} @ ${pos['entry_price']:,.2f}")
        
        # 获取未成交订单
        orders = client.get_open_orders()
        print(f"\n✅ 未成交订单: {len(orders)} 个")
        for order in orders:
            print(f"   {order['symbol']}: {order['side']} {order['amount']} @ ${order['price']:,.2f}")
        
        return free_balance
    except Exception as e:
        print(f"❌ 获取账户信息失败: {e}")
        return 0


def test_place_limit_order(client: HyperliquidSDKClient, current_price: float):
    """测试 3: 下限价单"""
    print_section("测试 3: 下限价单（买入）")
    
    if current_price is None:
        print("⚠️  跳过: 无法获取当前价格")
        return None
    
    # 设置一个远离市场价的限价单（不会立即成交）
    # 买入价格设置为当前价格的 80%（远低于市场价）
    limit_price = round(current_price * 0.8, 2)
    size = 0.001  # 最小交易量
    
    print(f"准备下单:")
    print(f"  交易对: BTC")
    print(f"  方向: 买入 (Long)")
    print(f"  数量: {size} BTC")
    print(f"  限价: ${limit_price:,.2f}")
    print(f"  当前价格: ${current_price:,.2f}")
    print(f"  价格差距: {((current_price - limit_price) / current_price * 100):.1f}%")
    
    try:
        # 使用官方 SDK 的 order 方法
        from hyperliquid.utils.signing import OrderType
        
        result = client.exchange.order(
            name="BTC",
            is_buy=True,
            sz=size,
            limit_px=limit_price,
            order_type=OrderType.LIMIT,
            reduce_only=False
        )
        
        print(f"\n✅ 下单成功!")
        print(f"   返回结果: {result}")
        
        # 等待一下让订单进入系统
        time.sleep(2)
        
        # 查询订单状态
        orders = client.get_open_orders("BTC")
        if orders:
            print(f"\n✅ 订单已确认:")
            for order in orders:
                print(f"   订单ID: {order['id']}")
                print(f"   {order['symbol']}: {order['side']} {order['amount']} @ ${order['price']:,.2f}")
                print(f"   已成交: {order['filled']}")
                print(f"   剩余: {order['remaining']}")
        
        return result
    except Exception as e:
        print(f"❌ 下单失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_query_orders(client: HyperliquidSDKClient):
    """测试 4: 查询订单"""
    print_section("测试 4: 查询所有未成交订单")
    
    try:
        orders = client.get_open_orders()
        
        if not orders:
            print("✅ 当前无未成交订单")
            return []
        
        print(f"✅ 找到 {len(orders)} 个未成交订单:")
        for i, order in enumerate(orders, 1):
            print(f"\n订单 {i}:")
            print(f"  订单ID: {order['id']}")
            print(f"  交易对: {order['symbol']}")
            print(f"  方向: {order['side']}")
            print(f"  类型: {order['type']}")
            print(f"  价格: ${order['price']:,.2f}")
            print(f"  数量: {order['amount']}")
            print(f"  已成交: {order['filled']}")
            print(f"  剩余: {order['remaining']}")
            print(f"  时间戳: {order['timestamp']}")
        
        return orders
    except Exception as e:
        print(f"❌ 查询订单失败: {e}")
        return []


def test_cancel_order(client: HyperliquidSDKClient, orders: list):
    """测试 5: 取消订单"""
    print_section("测试 5: 取消订单")
    
    if not orders:
        print("⚠️  跳过: 没有可取消的订单")
        return
    
    # 取消第一个订单
    order = orders[0]
    print(f"准备取消订单:")
    print(f"  订单ID: {order['id']}")
    print(f"  交易对: {order['symbol']}")
    print(f"  {order['side']} {order['amount']} @ ${order['price']:,.2f}")
    
    try:
        # 使用官方 SDK 的 cancel 方法
        result = client.exchange.cancel(
            name=order['symbol'],
            oid=int(order['id'])
        )
        
        print(f"\n✅ 取消订单成功!")
        print(f"   返回结果: {result}")
        
        # 等待一下
        time.sleep(2)
        
        # 验证订单已取消
        remaining_orders = client.get_open_orders(order['symbol'])
        print(f"\n✅ 剩余订单: {len(remaining_orders)} 个")
        
    except Exception as e:
        print(f"❌ 取消订单失败: {e}")
        import traceback
        traceback.print_exc()


def test_market_order(client: HyperliquidSDKClient, current_price: float):
    """测试 6: 市价单（谨慎使用）"""
    print_section("测试 6: 市价单（仅演示，不实际执行）")
    
    print("⚠️  市价单会立即成交，可能产生实际交易！")
    print("⚠️  此测试仅演示代码，不会实际执行")
    
    size = 0.001
    slippage = 0.05  # 5% 滑点
    
    print(f"\n市价单示例代码:")
    print(f"```python")
    print(f"# 市价买入")
    print(f"result = client.exchange.market_open(")
    print(f"    name='BTC',")
    print(f"    is_buy=True,")
    print(f"    sz={size},")
    print(f"    px={current_price},  # 参考价格")
    print(f"    slippage={slippage}  # 滑点容忍度")
    print(f")")
    print(f"")
    print(f"# 市价平仓")
    print(f"result = client.exchange.market_close(")
    print(f"    coin='BTC',")
    print(f"    sz={size},  # 平仓数量")
    print(f"    slippage={slippage}")
    print(f")")
    print(f"```")


def test_modify_leverage(client: HyperliquidSDKClient):
    """测试 7: 修改杠杆"""
    print_section("测试 7: 修改杠杆（仅演示）")

    print("⚠️  修改杠杆会影响账户风险，此测试仅演示代码")

    print(f"\n修改杠杆示例代码:")
    print(f"```python")
    print(f"# 使用便捷方法设置杠杆")
    print(f"result = client.set_leverage(")
    print(f"    symbol='BTC',")
    print(f"    leverage=5,")
    print(f"    is_cross=True  # True=全仓, False=逐仓")
    print(f")")
    print(f"```")


def test_advanced_features(client: HyperliquidSDKClient):
    """测试 8: 高级功能"""
    print_section("测试 8: 高级功能")

    try:
        # 获取资金费率
        print("📊 获取资金费率:")
        funding = client.get_funding_rate("BTC")
        print(f"   BTC 资金费率: {funding['funding_rate_percent']:.4f}%")

        funding_eth = client.get_funding_rate("ETH")
        print(f"   ETH 资金费率: {funding_eth['funding_rate_percent']:.4f}%")

        # 获取订单簿
        print(f"\n📖 获取订单簿 (前 5 档):")
        order_book = client.get_order_book("BTC", depth=5)

        print(f"\n   卖盘 (Asks):")
        for i, ask in enumerate(reversed(order_book['asks'][:5]), 1):
            print(f"   {i}. ${ask['price']:,.2f} - {ask['size']:.4f} BTC ({ask['orders']} 订单)")

        print(f"\n   买盘 (Bids):")
        for i, bid in enumerate(order_book['bids'][:5], 1):
            print(f"   {i}. ${bid['price']:,.2f} - {bid['size']:.4f} BTC ({bid['orders']} 订单)")

        print(f"\n✅ 高级功能测试完成")

    except Exception as e:
        print(f"❌ 高级功能测试失败: {e}")


def test_convenience_methods(client: HyperliquidSDKClient, current_price: float):
    """测试 9: 便捷方法"""
    print_section("测试 9: 便捷方法演示")

    print("✅ SDK 客户端提供了以下便捷方法:\n")

    print("1️⃣  下限价单:")
    print("```python")
    print("result = client.place_limit_order(")
    print("    symbol='BTC',")
    print("    side='buy',")
    print("    amount=0.001,")
    print(f"    price={current_price * 0.8:.2f}")
    print(")")
    print("```\n")

    print("2️⃣  下市价单:")
    print("```python")
    print("result = client.place_market_order(")
    print("    symbol='BTC',")
    print("    side='buy',")
    print("    amount=0.001,")
    print("    slippage=0.05")
    print(")")
    print("```\n")

    print("3️⃣  取消订单:")
    print("```python")
    print("result = client.cancel_order(")
    print("    symbol='BTC',")
    print("    order_id=12345")
    print(")")
    print("```\n")

    print("4️⃣  取消所有订单:")
    print("```python")
    print("# 取消所有 BTC 订单")
    print("result = client.cancel_all_orders(symbol='BTC')")
    print("")
    print("# 取消所有交易对的订单")
    print("result = client.cancel_all_orders()")
    print("```\n")

    print("5️⃣  平仓:")
    print("```python")
    print("# 全部平仓")
    print("result = client.close_position(symbol='BTC')")
    print("")
    print("# 部分平仓")
    print("result = client.close_position(symbol='BTC', amount=0.001)")
    print("```\n")

    print("6️⃣  设置杠杆:")
    print("```python")
    print("result = client.set_leverage(")
    print("    symbol='BTC',")
    print("    leverage=5,")
    print("    is_cross=True")
    print(")")
    print("```")


def main():
    """主测试函数"""
    print_section("Hyperliquid 永续合约交易功能测试")
    
    # 获取配置
    api_address = os.getenv("HYPERLIQUID_API_KEY")
    api_secret = os.getenv("HYPERLIQUID_API_SECRET")
    wallet_address = os.getenv("WALLET_ADDRESS")
    vault_address = os.getenv("VAULT_ADDRESS")
    testnet = os.getenv("HYPERLIQUID_TESTNET", "false").lower() == "true"
    
    if not api_address or not api_secret:
        print("❌ 错误: 请在 .env 文件中设置 HYPERLIQUID_API_KEY 和 HYPERLIQUID_API_SECRET")
        return
    
    print(f"✅ 配置信息:")
    print(f"   API 地址: {api_address}")
    print(f"   主钱包地址: {wallet_address or api_address}")
    print(f"   网络: {'测试网' if testnet else '主网'}")
    print(f"   Vault 地址: {vault_address or '未设置'}")
    
    # 创建客户端
    client = HyperliquidSDKClient(
        wallet_address=wallet_address or api_address,
        private_key=api_secret,
        vault_address=vault_address,
        testnet=testnet
    )
    
    # 运行测试
    current_price = test_get_current_price(client)
    free_balance = test_get_account_info(client)

    # 测试高级功能（不需要余额）
    test_advanced_features(client)

    if free_balance > 0:
        print(f"\n💰 账户有余额，可以进行交易测试")
        order_result = test_place_limit_order(client, current_price)
        orders = test_query_orders(client)
        if orders:
            test_cancel_order(client, orders)
    else:
        print(f"\n⚠️  账户余额为 0，跳过交易测试")
        print(f"   请先充值到测试网: https://app.hyperliquid-testnet.xyz/drip")

    test_market_order(client, current_price)
    test_modify_leverage(client)
    test_convenience_methods(client, current_price)

    print_section("测试完成")
    print("\n✅ 所有测试已完成!")
    print("\n📖 官方 SDK 原生方法:")
    print("   ✅ order() - 下限价单")
    print("   ✅ cancel() - 取消订单")
    print("   ✅ market_open() - 市价开仓")
    print("   ✅ market_close() - 市价平仓")
    print("   ✅ update_leverage() - 修改杠杆")
    print("   ✅ bulk_orders() - 批量下单")
    print("   ✅ bulk_cancel() - 批量取消")
    print("   ✅ modify_order() - 修改订单")
    print("\n📖 便捷方法（封装）:")
    print("   ✅ place_limit_order() - 下限价单")
    print("   ✅ place_market_order() - 下市价单")
    print("   ✅ cancel_order() - 取消订单")
    print("   ✅ cancel_all_orders() - 取消所有订单")
    print("   ✅ close_position() - 平仓")
    print("   ✅ set_leverage() - 设置杠杆")
    print("   ✅ get_funding_rate() - 获取资金费率")
    print("   ✅ get_order_book() - 获取订单簿")
    print("   ✅ get_user_state() - 获取用户状态")


if __name__ == "__main__":
    main()

