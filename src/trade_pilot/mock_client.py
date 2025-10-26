"""
Mock Hyperliquid 客户端
用于测试和开发，不需要真实的 API 密钥
"""
from typing import Optional, Dict, Any, List
import logging
import random
from datetime import datetime

logger = logging.getLogger(__name__)


class MockHyperliquidClient:
    """Mock Hyperliquid 交易客户端"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = True
    ):
        """
        初始化 Mock 客户端
        
        Args:
            api_key: API 密钥（Mock 模式下不需要）
            api_secret: API 密钥（Mock 模式下不需要）
            testnet: 是否使用测试网
        """
        self.testnet = testnet
        self.orders = {}  # 存储订单
        self.positions = {}  # 存储持仓
        self.order_counter = 1000
        
        # Mock 价格数据
        self.prices = {
            'BTC/USDT:USDT': 45000.0,
            'ETH/USDT:USDT': 2300.0,
            'SOL/USDT:USDT': 100.0,
        }
        
        logger.info(f"Mock Hyperliquid 客户端初始化完成 (testnet={testnet})")
    
    def get_balance(self) -> Dict[str, Any]:
        """获取账户余额（Mock）"""
        balance = {
            'total': {
                'USDT': 10000.0,
                'BTC': 0.5,
                'ETH': 2.0,
            },
            'free': {
                'USDT': 8000.0,
                'BTC': 0.3,
                'ETH': 1.5,
            },
            'used': {
                'USDT': 2000.0,
                'BTC': 0.2,
                'ETH': 0.5,
            }
        }
        logger.info(f"获取余额成功 (Mock): {balance.get('total', {})}")
        return balance
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """获取当前持仓（Mock）"""
        positions = [
            {
                'symbol': 'BTC/USDT:USDT',
                'side': 'long',
                'contracts': 0.1,
                'entryPrice': 44000.0,
                'markPrice': 45000.0,
                'unrealizedPnl': 100.0,
                'leverage': 5,
            },
            {
                'symbol': 'ETH/USDT:USDT',
                'side': 'short',
                'contracts': 1.0,
                'entryPrice': 2400.0,
                'markPrice': 2300.0,
                'unrealizedPnl': 100.0,
                'leverage': 3,
            }
        ]
        logger.info(f"获取持仓成功 (Mock): {len(positions)} 个持仓")
        return positions
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """获取交易对行情（Mock）"""
        base_price = self.prices.get(symbol, 1000.0)
        # 添加随机波动
        price = base_price * (1 + random.uniform(-0.01, 0.01))
        
        ticker = {
            'symbol': symbol,
            'last': price,
            'bid': price * 0.9999,
            'ask': price * 1.0001,
            'high': price * 1.02,
            'low': price * 0.98,
            'volume': random.uniform(1000, 10000),
            'timestamp': datetime.now().timestamp() * 1000,
        }
        logger.info(f"获取 {symbol} 行情成功 (Mock): {ticker.get('last')}")
        return ticker
    
    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """获取订单簿（Mock）"""
        base_price = self.prices.get(symbol, 1000.0)
        
        # 生成买单
        bids = []
        for i in range(limit):
            price = base_price * (1 - 0.0001 * (i + 1))
            amount = random.uniform(0.1, 2.0)
            bids.append([price, amount])
        
        # 生成卖单
        asks = []
        for i in range(limit):
            price = base_price * (1 + 0.0001 * (i + 1))
            amount = random.uniform(0.1, 2.0)
            asks.append([price, amount])
        
        orderbook = {
            'symbol': symbol,
            'bids': bids,
            'asks': asks,
            'timestamp': datetime.now().timestamp() * 1000,
        }
        logger.info(f"获取 {symbol} 订单簿成功 (Mock)")
        return orderbook
    
    def create_market_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        reduce_only: bool = False
    ) -> Dict[str, Any]:
        """创建市价单（Mock）"""
        order_id = f"mock_order_{self.order_counter}"
        self.order_counter += 1
        
        price = self.prices.get(symbol, 1000.0)
        
        order = {
            'id': order_id,
            'symbol': symbol,
            'type': 'market',
            'side': side,
            'amount': amount,
            'price': price,
            'status': 'closed',
            'filled': amount,
            'remaining': 0,
            'timestamp': datetime.now().timestamp() * 1000,
            'reduceOnly': reduce_only,
        }
        
        self.orders[order_id] = order
        logger.info(f"创建市价单成功 (Mock): {order_id} - {side} {amount} {symbol}")
        return order
    
    def create_limit_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        reduce_only: bool = False,
        post_only: bool = False
    ) -> Dict[str, Any]:
        """创建限价单（Mock）"""
        order_id = f"mock_order_{self.order_counter}"
        self.order_counter += 1
        
        order = {
            'id': order_id,
            'symbol': symbol,
            'type': 'limit',
            'side': side,
            'amount': amount,
            'price': price,
            'status': 'open',
            'filled': 0,
            'remaining': amount,
            'timestamp': datetime.now().timestamp() * 1000,
            'reduceOnly': reduce_only,
            'postOnly': post_only,
        }
        
        self.orders[order_id] = order
        logger.info(f"创建限价单成功 (Mock): {order_id} - {side} {amount} {symbol} @ {price}")
        return order
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """取消订单（Mock）"""
        if order_id in self.orders:
            self.orders[order_id]['status'] = 'canceled'
            logger.info(f"取消订单成功 (Mock): {order_id}")
            return {'id': order_id, 'status': 'canceled'}
        else:
            logger.warning(f"订单不存在 (Mock): {order_id}")
            return {'error': 'Order not found'}
    
    def cancel_all_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """取消所有订单（Mock）"""
        results = []
        for order_id, order in self.orders.items():
            if symbol is None or order['symbol'] == symbol:
                if order['status'] == 'open':
                    order['status'] = 'canceled'
                    results.append({'id': order_id, 'status': 'canceled'})
        
        logger.info(f"取消所有订单成功 (Mock): {symbol or '所有交易对'}, {len(results)} 个订单")
        return results
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取未成交订单（Mock）"""
        orders = []
        for order in self.orders.values():
            if order['status'] == 'open':
                if symbol is None or order['symbol'] == symbol:
                    orders.append(order)
        
        logger.info(f"获取未成交订单成功 (Mock): {len(orders)} 个订单")
        return orders
    
    def get_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """查询订单状态（Mock）"""
        if order_id in self.orders:
            order = self.orders[order_id]
            logger.info(f"查询订单状态成功 (Mock): {order_id} - {order.get('status')}")
            return order
        else:
            logger.warning(f"订单不存在 (Mock): {order_id}")
            return {'error': 'Order not found'}
    
    def close_position(self, symbol: str) -> Dict[str, Any]:
        """平仓（Mock）"""
        positions = self.get_positions()
        position = next((p for p in positions if p['symbol'] == symbol), None)
        
        if not position or position.get('contracts', 0) == 0:
            logger.warning(f"没有 {symbol} 的持仓 (Mock)")
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
        
        logger.info(f"平仓成功 (Mock): {symbol}")
        return order

