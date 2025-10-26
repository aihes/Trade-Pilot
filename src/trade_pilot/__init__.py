"""
Trade-Pilot: AI-Powered Trading Agent
"""
from .hyperliquid_client import HyperliquidClient
from .agent import TradingAgent
from .tools import create_trading_tools

__version__ = "0.1.0"
__all__ = [
    "HyperliquidClient",
    "TradingAgent",
    "create_trading_tools"
]


def main():
    """主入口函数"""
    import os
    import logging
    from dotenv import load_dotenv

    # 加载环境变量
    load_dotenv()

    # 配置日志
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 获取配置
    api_key = os.getenv("HYPERLIQUID_API_KEY")
    api_secret = os.getenv("HYPERLIQUID_API_SECRET")
    testnet = os.getenv("HYPERLIQUID_TESTNET", "true").lower() == "true"
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    model_name = os.getenv("MODEL_NAME", "anthropic/claude-3.5-sonnet")

    # 检查必要的配置
    if not openrouter_api_key:
        print("错误: 请设置 OPENROUTER_API_KEY 环境变量")
        return

    # 创建客户端
    client = HyperliquidClient(
        api_key=api_key,
        api_secret=api_secret,
        testnet=testnet
    )

    # 创建 Agent
    agent = TradingAgent(
        hyperliquid_client=client,
        openrouter_api_key=openrouter_api_key,
        model=model_name
    )

    # 启动交互式聊天
    agent.chat()


if __name__ == "__main__":
    main()
