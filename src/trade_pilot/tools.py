"""
LangChain 交易工具
将 Hyperliquid 客户端功能封装为 LangChain Tools
"""
from typing import Optional, Type, Any
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from .hyperliquid_client import HyperliquidClient
import json
import logging

logger = logging.getLogger(__name__)


# ============ 工具输入模型 ============

class PlaceOrderInput(BaseModel):
    """下单工具输入"""
    symbol: str = Field(description="交易对符号，如 'BTC/USDT:USDT'")
    side: str = Field(description="交易方向: 'buy' 或 'sell'")
    amount: float = Field(description="交易数量")
    order_type: str = Field(default="market", description="订单类型: 'market' 或 'limit'")
    price: Optional[float] = Field(default=None, description="限价单价格（仅限价单需要）")
    reduce_only: bool = Field(default=False, description="是否只减仓")


class CancelOrderInput(BaseModel):
    """取消订单工具输入"""
    order_id: str = Field(description="订单 ID")
    symbol: str = Field(description="交易对符号")


class QueryOrderInput(BaseModel):
    """查询订单工具输入"""
    order_id: str = Field(description="订单 ID")
    symbol: str = Field(description="交易对符号")


class GetOpenOrdersInput(BaseModel):
    """获取未成交订单工具输入"""
    symbol: Optional[str] = Field(default=None, description="交易对符号，不填则获取所有")


class GetPositionsInput(BaseModel):
    """获取持仓工具输入"""
    pass


class GetTickerInput(BaseModel):
    """获取行情工具输入"""
    symbol: str = Field(description="交易对符号，如 'BTC/USDT:USDT'")


class ClosePositionInput(BaseModel):
    """平仓工具输入"""
    symbol: str = Field(description="交易对符号")


# ============ LangChain 工具 ============

class PlaceOrderTool(BaseTool):
    """下单工具"""
    name: str = "place_order"
    description: str = """
    在 Hyperliquid 上下单（市价单或限价单）。
    使用 vault 账户执行交易。
    
    参数:
    - symbol: 交易对符号，如 'BTC/USDT:USDT'
    - side: 'buy' 买入或 'sell' 卖出
    - amount: 交易数量
    - order_type: 'market' 市价单或 'limit' 限价单
    - price: 限价单价格（仅限价单需要）
    - reduce_only: 是否只减仓（默认 False）
    
    返回: 订单信息（JSON 格式）
    """
    args_schema: Type[BaseModel] = PlaceOrderInput
    client: HyperliquidClient = Field(default=None)
    
    def __init__(self, client: HyperliquidClient):
        super().__init__(client=client)
    
    def _run(
        self,
        symbol: str,
        side: str,
        amount: float,
        order_type: str = "market",
        price: Optional[float] = None,
        reduce_only: bool = False
    ) -> str:
        """执行下单"""
        try:
            if order_type == "market":
                order = self.client.create_market_order(
                    symbol=symbol,
                    side=side,
                    amount=amount,
                    reduce_only=reduce_only
                )
            elif order_type == "limit":
                if price is None:
                    return json.dumps({"error": "限价单必须提供价格"}, ensure_ascii=False)
                order = self.client.create_limit_order(
                    symbol=symbol,
                    side=side,
                    amount=amount,
                    price=price,
                    reduce_only=reduce_only
                )
            else:
                return json.dumps({"error": f"不支持的订单类型: {order_type}"}, ensure_ascii=False)
            
            return json.dumps({
                "success": True,
                "order_id": order.get('id'),
                "symbol": order.get('symbol'),
                "side": order.get('side'),
                "amount": order.get('amount'),
                "price": order.get('price'),
                "status": order.get('status'),
                "type": order.get('type')
            }, ensure_ascii=False)
        except Exception as e:
            logger.error(f"下单失败: {e}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)


class CancelOrderTool(BaseTool):
    """取消订单工具"""
    name: str = "cancel_order"
    description: str = """
    取消指定的订单。
    
    参数:
    - order_id: 订单 ID
    - symbol: 交易对符号
    
    返回: 取消结果（JSON 格式）
    """
    args_schema: Type[BaseModel] = CancelOrderInput
    client: HyperliquidClient = Field(default=None)
    
    def __init__(self, client: HyperliquidClient):
        super().__init__(client=client)
    
    def _run(self, order_id: str, symbol: str) -> str:
        """执行取消订单"""
        try:
            result = self.client.cancel_order(order_id, symbol)
            return json.dumps({
                "success": True,
                "order_id": order_id,
                "symbol": symbol,
                "result": result
            }, ensure_ascii=False)
        except Exception as e:
            logger.error(f"取消订单失败: {e}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)


class QueryOrderStatusTool(BaseTool):
    """查询订单状态工具"""
    name: str = "query_order_status"
    description: str = """
    查询指定订单的状态。
    
    参数:
    - order_id: 订单 ID
    - symbol: 交易对符号
    
    返回: 订单详细信息（JSON 格式）
    """
    args_schema: Type[BaseModel] = QueryOrderInput
    client: HyperliquidClient = Field(default=None)
    
    def __init__(self, client: HyperliquidClient):
        super().__init__(client=client)
    
    def _run(self, order_id: str, symbol: str) -> str:
        """执行查询订单状态"""
        try:
            order = self.client.get_order_status(order_id, symbol)
            return json.dumps({
                "success": True,
                "order_id": order.get('id'),
                "symbol": order.get('symbol'),
                "side": order.get('side'),
                "type": order.get('type'),
                "amount": order.get('amount'),
                "price": order.get('price'),
                "filled": order.get('filled'),
                "remaining": order.get('remaining'),
                "status": order.get('status'),
                "timestamp": order.get('timestamp')
            }, ensure_ascii=False)
        except Exception as e:
            logger.error(f"查询订单状态失败: {e}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)


class GetOpenOrdersTool(BaseTool):
    """获取未成交订单工具"""
    name: str = "get_open_orders"
    description: str = """
    获取当前所有未成交的订单。
    
    参数:
    - symbol: 交易对符号（可选，不填则获取所有交易对的订单）
    
    返回: 订单列表（JSON 格式）
    """
    args_schema: Type[BaseModel] = GetOpenOrdersInput
    client: HyperliquidClient = Field(default=None)
    
    def __init__(self, client: HyperliquidClient):
        super().__init__(client=client)
    
    def _run(self, symbol: Optional[str] = None) -> str:
        """执行获取未成交订单"""
        try:
            orders = self.client.get_open_orders(symbol)
            orders_info = [{
                "order_id": o.get('id'),
                "symbol": o.get('symbol'),
                "side": o.get('side'),
                "type": o.get('type'),
                "amount": o.get('amount'),
                "price": o.get('price'),
                "filled": o.get('filled'),
                "remaining": o.get('remaining'),
                "status": o.get('status')
            } for o in orders]
            
            return json.dumps({
                "success": True,
                "count": len(orders_info),
                "orders": orders_info
            }, ensure_ascii=False)
        except Exception as e:
            logger.error(f"获取未成交订单失败: {e}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)


class GetPositionsTool(BaseTool):
    """获取持仓工具"""
    name: str = "get_positions"
    description: str = """
    获取当前所有持仓信息。
    
    返回: 持仓列表（JSON 格式）
    """
    args_schema: Type[BaseModel] = GetPositionsInput
    client: HyperliquidClient = Field(default=None)
    
    def __init__(self, client: HyperliquidClient):
        super().__init__(client=client)
    
    def _run(self) -> str:
        """执行获取持仓"""
        try:
            positions = self.client.get_positions()
            positions_info = [{
                "symbol": p.get('symbol'),
                "side": p.get('side'),
                "contracts": p.get('contracts'),
                "entry_price": p.get('entryPrice'),
                "mark_price": p.get('markPrice'),
                "unrealized_pnl": p.get('unrealizedPnl'),
                "percentage": p.get('percentage')
            } for p in positions if p.get('contracts', 0) != 0]
            
            return json.dumps({
                "success": True,
                "count": len(positions_info),
                "positions": positions_info
            }, ensure_ascii=False)
        except Exception as e:
            logger.error(f"获取持仓失败: {e}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)


class GetTickerTool(BaseTool):
    """获取行情工具"""
    name: str = "get_ticker"
    description: str = """
    获取指定交易对的实时行情数据。
    
    参数:
    - symbol: 交易对符号，如 'BTC/USDT:USDT'
    
    返回: 行情数据（JSON 格式）
    """
    args_schema: Type[BaseModel] = GetTickerInput
    client: HyperliquidClient = Field(default=None)
    
    def __init__(self, client: HyperliquidClient):
        super().__init__(client=client)
    
    def _run(self, symbol: str) -> str:
        """执行获取行情"""
        try:
            ticker = self.client.get_ticker(symbol)
            return json.dumps({
                "success": True,
                "symbol": ticker.get('symbol'),
                "last": ticker.get('last'),
                "bid": ticker.get('bid'),
                "ask": ticker.get('ask'),
                "high": ticker.get('high'),
                "low": ticker.get('low'),
                "volume": ticker.get('volume'),
                "timestamp": ticker.get('timestamp')
            }, ensure_ascii=False)
        except Exception as e:
            logger.error(f"获取行情失败: {e}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)


class ClosePositionTool(BaseTool):
    """平仓工具"""
    name: str = "close_position"
    description: str = """
    平掉指定交易对的持仓。
    
    参数:
    - symbol: 交易对符号
    
    返回: 平仓结果（JSON 格式）
    """
    args_schema: Type[BaseModel] = ClosePositionInput
    client: HyperliquidClient = Field(default=None)
    
    def __init__(self, client: HyperliquidClient):
        super().__init__(client=client)
    
    def _run(self, symbol: str) -> str:
        """执行平仓"""
        try:
            result = self.client.close_position(symbol)
            if result.get('status') == 'no_position':
                return json.dumps({
                    "success": False,
                    "message": f"没有 {symbol} 的持仓"
                }, ensure_ascii=False)
            
            return json.dumps({
                "success": True,
                "symbol": symbol,
                "order_id": result.get('id'),
                "message": "平仓成功"
            }, ensure_ascii=False)
        except Exception as e:
            logger.error(f"平仓失败: {e}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)


def create_trading_tools(client: HyperliquidClient) -> list:
    """
    创建所有交易工具
    
    Args:
        client: Hyperliquid 客户端实例
        
    Returns:
        工具列表
    """
    return [
        PlaceOrderTool(client=client),
        CancelOrderTool(client=client),
        QueryOrderStatusTool(client=client),
        GetOpenOrdersTool(client=client),
        GetPositionsTool(client=client),
        GetTickerTool(client=client),
        ClosePositionTool(client=client)
    ]

