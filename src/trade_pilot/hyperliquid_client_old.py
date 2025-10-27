"""
Hyperliquid 交易客户端封装
使用 CCXT 库与 Hyperliquid 交易所进行交互
"""
import ccxt
from typing import Optional, Dict, Any, List
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class HyperliquidClient:
    """Hyperliquid 交易客户端"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = True
    ):
        """
        初始化 Hyperliquid 客户端
        
        Args:
            api_key: API 密钥
            api_secret: API 密钥
            testnet: 是否使用测试网
        """
        self.testnet = testnet
        
        # 初始化 CCXT Hyperliquid 客户端
        self.exchange = ccxt.hyperliquid({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'swap',  # 永续合约
                'testnet': testnet
            }
        })
        
        logger.info(f"Hyperliquid 客户端初始化完成 (testnet={testnet})")
    
    def get_balance(self) -> Dict[str, Any]:
        """
        获取账户余额
        
        Returns:
            账户余额信息
        """
        try:
            balance = self.exchange.fetch_balance()
            logger.info(f"获取余额成功: {balance.get('total', {})}")
            return balance
        except Exception as e:
            logger.error(f"获取余额失败: {e}")
            raise
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        获取当前持仓
        
        Returns:
            持仓列表
        """
        try:
            positions = self.exchange.fetch_positions()
            logger.info(f"获取持仓成功: {len(positions)} 个持仓")
            return positions
        except Exception as e:
            logger.error(f"获取持仓失败: {e}")
            raise
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        获取交易对行情
        
        Args:
            symbol: 交易对符号，如 'BTC/USDT:USDT'
            
        Returns:
            行情数据
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            logger.info(f"获取 {symbol} 行情成功: {ticker.get('last')}")
            return ticker
        except Exception as e:
            logger.error(f"获取 {symbol} 行情失败: {e}")
            raise
    
    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """
        获取订单簿
        
        Args:
            symbol: 交易对符号
            limit: 深度限制
            
        Returns:
            订单簿数据
        """
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit)
            logger.info(f"获取 {symbol} 订单簿成功")
            return orderbook
        except Exception as e:
            logger.error(f"获取 {symbol} 订单簿失败: {e}")
            raise
    
    def create_market_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        reduce_only: bool = False
    ) -> Dict[str, Any]:
        """
        创建市价单
        
        Args:
            symbol: 交易对符号，如 'BTC/USDT:USDT'
            side: 'buy' 或 'sell'
            amount: 数量
            reduce_only: 是否只减仓
            
        Returns:
            订单信息
        """
        try:
            params = {'reduceOnly': reduce_only} if reduce_only else {}
            order = self.exchange.create_market_order(
                symbol=symbol,
                side=side,
                amount=amount,
                params=params
            )
            logger.info(f"创建市价单成功: {order.get('id')} - {side} {amount} {symbol}")
            return order
        except Exception as e:
            logger.error(f"创建市价单失败: {e}")
            raise
    
    def create_limit_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        reduce_only: bool = False,
        post_only: bool = False
    ) -> Dict[str, Any]:
        """
        创建限价单
        
        Args:
            symbol: 交易对符号
            side: 'buy' 或 'sell'
            amount: 数量
            price: 价格
            reduce_only: 是否只减仓
            post_only: 是否只做 Maker
            
        Returns:
            订单信息
        """
        try:
            params = {}
            if reduce_only:
                params['reduceOnly'] = True
            if post_only:
                params['postOnly'] = True
                
            order = self.exchange.create_limit_order(
                symbol=symbol,
                side=side,
                amount=amount,
                price=price,
                params=params
            )
            logger.info(f"创建限价单成功: {order.get('id')} - {side} {amount} {symbol} @ {price}")
            return order
        except Exception as e:
            logger.error(f"创建限价单失败: {e}")
            raise
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        取消订单
        
        Args:
            order_id: 订单 ID
            symbol: 交易对符号
            
        Returns:
            取消结果
        """
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            logger.info(f"取消订单成功: {order_id}")
            return result
        except Exception as e:
            logger.error(f"取消订单失败: {e}")
            raise
    
    def cancel_all_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        取消所有订单
        
        Args:
            symbol: 交易对符号，如果为 None 则取消所有交易对的订单
            
        Returns:
            取消结果列表
        """
        try:
            result = self.exchange.cancel_all_orders(symbol)
            logger.info(f"取消所有订单成功: {symbol or '所有交易对'}")
            return result
        except Exception as e:
            logger.error(f"取消所有订单失败: {e}")
            raise
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取未成交订单
        
        Args:
            symbol: 交易对符号，如果为 None 则获取所有交易对的订单
            
        Returns:
            订单列表
        """
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            logger.info(f"获取未成交订单成功: {len(orders)} 个订单")
            return orders
        except Exception as e:
            logger.error(f"获取未成交订单失败: {e}")
            raise
    
    def get_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """
        查询订单状态
        
        Args:
            order_id: 订单 ID
            symbol: 交易对符号
            
        Returns:
            订单详情
        """
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            logger.info(f"查询订单状态成功: {order_id} - {order.get('status')}")
            return order
        except Exception as e:
            logger.error(f"查询订单状态失败: {e}")
            raise
    
    def close_position(self, symbol: str) -> Dict[str, Any]:
        """
        平仓
        
        Args:
            symbol: 交易对符号
            
        Returns:
            平仓结果
        """
        try:
            # 获取当前持仓
            positions = self.get_positions()
            position = next((p for p in positions if p['symbol'] == symbol), None)
            
            if not position or position.get('contracts', 0) == 0:
                logger.warning(f"没有 {symbol} 的持仓")
                return {'status': 'no_position'}
            
            # 确定平仓方向和数量
            contracts = abs(position['contracts'])
            side = 'sell' if position['side'] == 'long' else 'buy'
            
            # 创建市价平仓单
            order = self.create_market_order(
                symbol=symbol,
                side=side,
                amount=contracts,
                reduce_only=True
            )
            
            logger.info(f"平仓成功: {symbol}")
            return order
        except Exception as e:
            logger.error(f"平仓失败: {e}")
            raise

