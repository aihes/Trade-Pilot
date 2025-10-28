"""
基础使用示例
演示如何使用 Trade-Pilot 进行交易
"""
import os
import logging
from dotenv import load_dotenv
from trade_pilot import HyperliquidClient, TradingAgent

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
    # 检查是否有认证信息
    wallet_address = os.getenv("HYPERLIQUID_API_KEY")
    private_key = os.getenv("HYPERLIQUID_API_SECRET")
    
    if wallet_address and private_key:
        # 有认证信息，使用钱包模式
        print("使用钱包认证模式")
        client = HyperliquidClient(
            wallet_address=wallet_address,
            private_key=private_key,
            testnet=True
        )
    else:
        # 没有认证信息，使用只读模式（需要提供钱包地址查询余额等）
        print("警告：未设置认证信息，使用只读模式")
        print("如需查询账户余额等，请在 .env 文件中设置 HYPERLIQUID_WALLET_ADDRESS")
        
        # 即使只读模式，也尝试使用钱包地址（如果有的话）用于查询
        if wallet_address:
            client = HyperliquidClient(
                wallet_address=wallet_address,
                read_only=True,
                testnet=True
            )
        else:
            # 完全没有钱包地址，使用纯只读模式
            client = HyperliquidClient(
                read_only=True,
                testnet=True
            )
    
    
    # 2. 获取账户余额
    print("\n=== 账户总余额 ===")
    try:
        balance = client.get_balance()
        print(f"总余额: {balance.get('total', {})}")
        print(f"可用余额: {balance.get('free', {})}")
        print(f"已用余额: {balance.get('used', {})}")
    except Exception as e:
        print(f"获取总余额失败: {e}")
    
    # 3. 获取 BTC 行情
    print("\n=== BTC 行情 ===")
    ticker = client.get_ticker("BTC/USDC:USDC")
    print(f"最新价: {ticker.get('last')}")
    print(f"买一价: {ticker.get('bid')}")
    print(f"卖一价: {ticker.get('ask')}")
    
    # 4. 获取当前持仓
    print("\n=== 当前持仓 ===")
    positions = client.get_positions()
    for pos in positions:
        if pos.get('contracts', 0) != 0:
            print(f"{pos['symbol']}: {pos['side']} {pos['contracts']} 张")
    
    # 5. 获取未成交订单
    print("\n=== 未成交订单 ===")
    orders = client.get_open_orders()
    print(f"共 {len(orders)} 个未成交订单")


def example_agent_trading():
    """使用 Agent 进行交易"""
    
    # 1. 创建客户端
    # 选项 1: 使用钱包地址 + 私钥认证（需要交易功能时）
    wallet_address = os.getenv("HYPERLIQUID_API_KEY")
    private_key = os.getenv("HYPERLIQUID_API_SECRET")
    client = HyperliquidClient(
        wallet_address=wallet_address,
        private_key=private_key,
        testnet=True  # 使用测试网
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
    # 选项 1: 使用钱包地址 + 私钥认证（需要交易功能时）
    wallet_address = os.getenv("HYPERLIQUID_API_KEY")
    private_key = os.getenv("HYPERLIQUID_API_SECRET")
    client = HyperliquidClient(
        wallet_address=wallet_address,
        private_key=private_key,
        testnet=True
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

