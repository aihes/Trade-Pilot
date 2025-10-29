"""
基础使用示例
演示如何使用 Trade-Pilot 进行交易
使用 Hyperliquid 官方 SDK（推荐）
"""
import os
import logging
from dotenv import load_dotenv
from trade_pilot import HyperliquidSDKClient, TradingAgent

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_basic_trading():
    """基础交易示例"""

    # 1. 创建 Hyperliquid 客户端
    # 优先使用 API Wallet 配置（官方推荐）
    api_address = os.getenv("HYPERLIQUID_API_KEY")
    api_secret = os.getenv("HYPERLIQUID_API_SECRET")
    wallet_address = os.getenv("WALLET_ADDRESS")
    vault_address = os.getenv("VAULT_ADDRESS")
    testnet = os.getenv("HYPERLIQUID_TESTNET", "false").lower() == "true"

    if api_address and api_secret:
        # 使用 API Wallet 模式（官方推荐）
        print(f"✅ 使用 API Wallet 认证模式")
        print(f"   API 地址: {api_address}")
        print(f"   主钱包地址: {wallet_address or api_address}")
        print(f"   网络: {'测试网' if testnet else '主网'}")

        client = HyperliquidSDKClient(
            wallet_address=wallet_address or api_address,  # 如果没有指定主钱包，使用 API 地址
            private_key=api_secret,
            vault_address=vault_address,  # 如果有 vault_address，则代理子账户
            testnet=testnet
        )
    else:
        # 没有认证信息，使用只读模式
        print("⚠️  警告：未设置认证信息，使用只读模式")
        print("   如需交易功能，请在 .env 文件中设置 HYPERLIQUID_API_KEY 和 HYPERLIQUID_API_SECRET")
        client = HyperliquidSDKClient(
            read_only=True,
            testnet=testnet
        )
    
    
    # 2. 获取账户余额
    print("\n=== 账户余额 ===")
    try:
        balance = client.fetch_balance()
        if 'total' in balance and balance['total']:
            for currency, amount in balance['total'].items():
                print(f"  {currency}: {amount:,.2f}")
        else:
            print("  无余额数据")
    except Exception as e:
        print(f"  ❌ 获取余额失败: {e}")
    
    # 3. 获取 BTC 行情
    print("\n=== BTC 行情 ===")
    try:
        price = client.get_current_price("BTC/USDC:USDC")
        print(f"  当前价格: ${price:,.2f}")
    except Exception as e:
        print(f"  ❌ 获取价格失败: {e}")

    # 4. 获取当前持仓（所有持仓）
    print("\n=== 当前持仓 ===")
    try:
        # 使用 get_all_positions() 获取所有持仓
        if hasattr(client, 'get_all_positions'):
            positions = client.get_all_positions()
        else:
            # 如果没有 get_all_positions，尝试获取常见交易对的持仓
            common_symbols = ["BTC/USDC:USDC", "ETH/USDC:USDC", "SOL/USDC:USDC"]
            positions = client.fetch_positions(common_symbols)

        if positions:
            for pos in positions:
                contracts = abs(float(pos.get('contracts', 0)))
                if contracts > 0:
                    print(f"  {pos.get('symbol')}: {pos.get('side')} {contracts} 张")
        else:
            print("  无持仓")
    except Exception as e:
        print(f"  ❌ 获取持仓失败: {e}")

    # 5. 获取未成交订单
    print("\n=== 未成交订单 ===")
    try:
        orders = client.get_open_orders()
        if orders:
            print(f"  共 {len(orders)} 个未成交订单")
            for order in orders[:5]:  # 只显示前5个
                print(f"  - {order.get('symbol')}: {order.get('side')} {order.get('amount')} @ {order.get('price')}")
        else:
            print("  无未成交订单")
    except Exception as e:
        print(f"  ❌ 获取订单失败: {e}")


def example_agent_trading():
    """使用 Agent 进行交易"""

    # 1. 创建客户端
    api_address = os.getenv("HYPERLIQUID_API_KEY")
    api_secret = os.getenv("HYPERLIQUID_API_SECRET")
    wallet_address = os.getenv("WALLET_ADDRESS")
    vault_address = os.getenv("VAULT_ADDRESS")
    testnet = os.getenv("HYPERLIQUID_TESTNET", "false").lower() == "true"

    if not api_address or not api_secret:
        print("❌ 错误：Agent 需要 API Wallet 认证")
        print("   请在 .env 文件中设置 HYPERLIQUID_API_KEY 和 HYPERLIQUID_API_SECRET")
        return

    client = HyperliquidSDKClient(
        wallet_address=wallet_address or api_address,
        private_key=api_secret,
        vault_address=vault_address,
        testnet=testnet
    )
    
    # 2. 创建 Agent
    agent = TradingAgent(
        hyperliquid_client=client,
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        model=os.getenv("MODEL_NAME")
    )
    
    # 3. 使用 Agent 查询信息
    print("\n=== Agent 查询示例 ===")
    response = agent.run("帮我查看一下 BTC 的当前价格")
    print(f"Agent: {response}")
    
    # 4. 使用 Agent 查询持仓
    print("\n=== Agent 持仓查询 ===")
    response = agent.run("我现在有哪些持仓？")
    print(f"Agent: {response}")


def example_interactive_chat():
    """交互式聊天示例"""

    # 创建客户端
    api_address = os.getenv("HYPERLIQUID_API_KEY")
    api_secret = os.getenv("HYPERLIQUID_API_SECRET")
    wallet_address = os.getenv("WALLET_ADDRESS")
    vault_address = os.getenv("VAULT_ADDRESS")
    testnet = os.getenv("HYPERLIQUID_TESTNET", "false").lower() == "true"

    if not api_address or not api_secret:
        print("❌ 错误：交互式聊天需要 API Wallet 认证")
        print("   请在 .env 文件中设置 HYPERLIQUID_API_KEY 和 HYPERLIQUID_API_SECRET")
        return

    client = HyperliquidSDKClient(
        wallet_address=wallet_address or api_address,
        private_key=api_secret,
        vault_address=vault_address,
        testnet=testnet
    )
    
    # 创建 Agent
    agent = TradingAgent(
        hyperliquid_client=client,
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        model="anthropic/claude-3.5-sonnet"
    )
    
    # 启动交互式聊天
    agent.chat()


if __name__ == "__main__":
    print("Trade-Pilot 使用示例")
    print("=" * 50)
    print("1. 基础交易示例")
    print("2. Agent 交易示例")
    print("3. 交互式聊天")
    print("=" * 50)
    
    choice = input("请选择示例 (1/2/3): ").strip()
    
    if choice == "1":
        example_basic_trading()
    elif choice == "2":
        example_agent_trading()
    elif choice == "3":
        example_interactive_chat()
    else:
        print("无效选择")

