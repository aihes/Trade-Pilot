"""
测试 Trade Agent
使用 Mock 客户端进行测试，不需要真实的 API 密钥
"""
import os
import sys
import logging
from dotenv import load_dotenv

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.trade_pilot import MockHyperliquidClient, TradingAgent

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_agent():
    """测试 Agent 功能"""
    
    print("=" * 60)
    print("Trade-Pilot Agent 测试")
    print("=" * 60)
    print()
    
    # 1. 创建 Mock 客户端
    print("1. 创建 Mock 客户端...")
    client = MockHyperliquidClient(testnet=True)
    print("✓ Mock 客户端创建成功\n")
    
    # 2. 获取 OpenRouter API Key (优先使用 OPENROUTER_API_KEY)
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not openrouter_api_key:
        print("错误: 请在 .env 文件中设置 OPENROUTER_API_KEY")
        return

    print(f"2. 使用 OpenRouter API Key: {openrouter_api_key[:20]}...\n")
    
    # 3. 创建 Agent
    print("3. 创建 Trading Agent...")
    try:
        agent = TradingAgent(
            hyperliquid_client=client,
            openrouter_api_key=openrouter_api_key,
            model="anthropic/claude-3.5-sonnet"
        )
        print("✓ Agent 创建成功\n")
    except Exception as e:
        print(f"✗ Agent 创建失败: {e}\n")
        logger.error(f"Agent 创建失败: {e}", exc_info=True)
        return
    
    # 4. 测试查询功能
    print("=" * 60)
    print("测试 1: 查询 BTC 价格")
    print("=" * 60)
    try:
        response = agent.run("帮我查看 BTC 的当前价格")
        print(f"\n用户: 帮我查看 BTC 的当前价格")
        print(f"Agent: {response}\n")
    except Exception as e:
        print(f"✗ 测试失败: {e}\n")
        logger.error(f"测试失败: {e}", exc_info=True)
    
    # 5. 测试持仓查询
    print("=" * 60)
    print("测试 2: 查询持仓")
    print("=" * 60)
    try:
        response = agent.run("我现在有哪些持仓？")
        print(f"\n用户: 我现在有哪些持仓？")
        print(f"Agent: {response}\n")
    except Exception as e:
        print(f"✗ 测试失败: {e}\n")
        logger.error(f"测试失败: {e}", exc_info=True)
    
    # 6. 测试余额查询
    print("=" * 60)
    print("测试 3: 查询账户余额")
    print("=" * 60)
    try:
        response = agent.run("查看我的账户余额")
        print(f"\n用户: 查看我的账户余额")
        print(f"Agent: {response}\n")
    except Exception as e:
        print(f"✗ 测试失败: {e}\n")
        logger.error(f"测试失败: {e}", exc_info=True)
    
    # 7. 交互式模式提示
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)
    print()
    print("如果要启动交互式聊天，请运行:")
    print("  python examples/test_agent.py --chat")
    print()


def interactive_chat():
    """启动交互式聊天"""

    # 创建 Mock 客户端
    client = MockHyperliquidClient(testnet=True)

    # 获取 API Key (优先使用 OPENROUTER_API_KEY)
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not openrouter_api_key:
        print("错误: 请在 .env 文件中设置 OPENROUTER_API_KEY")
        return
    
    # 创建 Agent
    try:
        agent = TradingAgent(
            hyperliquid_client=client,
            openrouter_api_key=openrouter_api_key,
            model="anthropic/claude-3.5-sonnet"
        )
    except Exception as e:
        print(f"Agent 创建失败: {e}")
        logger.error(f"Agent 创建失败: {e}", exc_info=True)
        return
    
    # 启动交互式聊天
    print("\n提示: 这是 Mock 模式，所有交易数据都是模拟的\n")
    agent.chat()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--chat":
        interactive_chat()
    else:
        test_agent()

