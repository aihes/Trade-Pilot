"""
交易 Agent
使用 LangGraph 构建智能交易代理
"""
from typing import TypedDict, Annotated, Sequence
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END
import operator
import logging
from .hyperliquid_client import HyperliquidClient
from .tools import create_trading_tools

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """Agent 状态"""
    messages: Annotated[Sequence[HumanMessage | AIMessage | SystemMessage], operator.add]
    next: str


class TradingAgent:
    """交易 Agent"""
    
    def __init__(
        self,
        hyperliquid_client: HyperliquidClient,
        openrouter_api_key: str,
        model: str = "anthropic/claude-3.5-sonnet"
    ):
        """
        初始化交易 Agent
        
        Args:
            hyperliquid_client: Hyperliquid 客户端
            openrouter_api_key: OpenRouter API 密钥
            model: 使用的模型名称
        """
        self.client = hyperliquid_client

        # 创建交易工具
        self.tools = create_trading_tools(hyperliquid_client)

        # 初始化 LLM（通过 OpenRouter）
        self.llm = ChatOpenAI(
            model=model,
            openai_api_key=openrouter_api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.7
        )
        
        # 绑定工具到 LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 构建 LangGraph
        self.graph = self._build_graph()
        
        logger.info(f"交易 Agent 初始化完成，使用模型: {model}")
    
    def _build_graph(self) -> StateGraph:
        """构建 LangGraph 工作流"""
        
        # 定义节点函数
        def call_model(state: AgentState):
            """调用模型节点"""
            messages = state["messages"]
            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}
        
        def call_tool(state: AgentState):
            """调用工具节点"""
            messages = state["messages"]
            last_message = messages[-1]

            # 执行工具调用
            tool_calls = last_message.tool_calls
            tool_messages = []

            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                # 查找并执行工具
                tool = next((t for t in self.tools if t.name == tool_name), None)
                if tool:
                    result = tool.invoke(tool_args)
                    # 创建 ToolMessage
                    tool_message = ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"]
                    )
                    tool_messages.append(tool_message)

            # 返回工具执行结果
            return {"messages": tool_messages}
        
        def should_continue(state: AgentState):
            """判断是否继续"""
            messages = state["messages"]
            last_message = messages[-1]
            
            # 如果没有工具调用，结束
            if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
                return "end"
            return "continue"
        
        # 创建图
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("agent", call_model)
        workflow.add_node("action", call_tool)
        
        # 设置入口点
        workflow.set_entry_point("agent")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "continue": "action",
                "end": END
            }
        )
        
        # 添加普通边
        workflow.add_edge("action", "agent")
        
        return workflow.compile()
    
    def run(self, user_input: str, system_prompt: str = None) -> str:
        """
        运行 Agent
        
        Args:
            user_input: 用户输入
            system_prompt: 系统提示词
            
        Returns:
            Agent 响应
        """
        messages = []
        
        # 添加系统提示词
        if system_prompt is None:
            system_prompt = """你是一个专业的加密货币交易助手。
                                你可以帮助用户在 Hyperliquid 平台上执行交易操作。
                                请将USDT统一换成USDC, 因为HyperLiquid只支持USDC。
                                
                                你有以下能力：
                                1. 下单（市价单和限价单）
                                2. 取消订单
                                3. 查询订单状态
                                4. 获取未成交订单列表
                                5. 获取当前持仓
                                6. 获取实时行情
                                7. 平仓
                                
                                在执行交易操作前，请务必：
                                - 确认用户的交易意图
                                - 检查当前市场行情
                                - 评估风险
                                - 向用户说明操作的影响
                                
                                请谨慎操作，确保用户理解每一步的含义。"""
        
        messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=user_input))
        
        # 运行图
        try:
            result = self.graph.invoke({"messages": messages})
            
            # 提取最后的 AI 消息
            final_messages = result["messages"]
            ai_messages = [m for m in final_messages if isinstance(m, AIMessage)]
            
            if ai_messages:
                return ai_messages[-1].content
            else:
                return "抱歉，我无法处理您的请求。"
                
        except Exception as e:
            logger.error(f"Agent 运行失败: {e}")
            return f"发生错误: {str(e)}"
    
    def chat(self, system_prompt: str = None):
        """
        启动交互式聊天
        
        Args:
            system_prompt: 系统提示词
        """
        print("=" * 50)
        print("Trade-Pilot 交易助手")
        print("=" * 50)
        print("输入 'quit' 或 'exit' 退出")
        print()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("再见！")
                    break
                
                if not user_input:
                    continue
                
                response = self.run(user_input, system_prompt)
                print(f"\nAgent: {response}\n")
                
            except KeyboardInterrupt:
                print("\n再见！")
                break
            except Exception as e:
                logger.error(f"聊天错误: {e}")
                print(f"错误: {e}\n")

