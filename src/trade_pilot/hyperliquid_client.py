"""
Hyperliquid 交易客户端封装
使用 CCXT 库与 Hyperliquid 交易所进行交互
支持钱包地址+私钥认证方式
"""
import ccxt
import pandas as pd
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

#https://docs.ccxt.com/#/exchanges/hyperliquid?id=createvault
class HyperliquidClient:
    """
    Hyperliquid 交易客户端

    支持三种认证方式：
    1. 钱包地址 + 私钥（推荐，用于交易）
    2. API Key + Secret（官方 API 方式）
    3. 只读模式（不需要认证，仅查询公开数据）
    """

    def __init__(
        self,
        wallet_address: Optional[str] = None,
        private_key: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = False,
        read_only: bool = False
    ):
        """
        初始化 Hyperliquid 客户端

        Args:
            wallet_address: 钱包地址（用于钱包认证方式）
            private_key: 钱包私钥（用于钱包认证方式）
            api_key: API 密钥（用于 API 认证方式）
            api_secret: API 密钥（用于 API 认证方式）
            testnet: 是否使用测试网
            read_only: 只读模式（不需要认证，仅查询公开数据）

        认证方式优先级：
        1. 钱包地址 + 私钥（最推荐）
        2. API Key + Secret
        3. 只读模式
        """
        self.testnet = testnet
        self.read_only = read_only

        # 方式 1: 钱包地址 + 私钥（推荐用于交易）
        if wallet_address and private_key:
            logger.info("使用钱包地址 + 私钥认证")
            self.exchange = ccxt.hyperliquid({
                "walletAddress": wallet_address,
                "privateKey": private_key,
                "enableRateLimit": True,
            })
            self.auth_method = "wallet"

        # 方式 2: API Key + Secret（官方 API 方式）
        elif api_key and api_secret:
            logger.info("使用 API Key + Secret 认证")
            self.exchange = ccxt.hyperliquid({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'swap',  # 永续合约
                    'testnet': testnet
                }
            })
            self.auth_method = "api"

        # 方式 3: 只读模式（仅查询公开数据）
        elif read_only:
            logger.info("使用只读模式（无认证）")
            self.exchange = ccxt.hyperliquid({
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'swap',
                    'testnet': testnet
                }
            })
            self.auth_method = "readonly"

        else:
            raise ValueError(
                "需要提供以下认证方式之一：\n"
                "1. wallet_address + private_key（推荐）\n"
                "2. api_key + api_secret\n"
                "3. read_only=True（只读模式）"
            )

        # 加载市场数据
        self.markets = {}
        self._load_markets()

        logger.info(f"Hyperliquid 客户端初始化完成 (认证方式={self.auth_method}, testnet={testnet})")
    
    def _load_markets(self) -> None:
        """加载市场数据"""
        try:
            self.markets = self.exchange.load_markets()
            logger.info(f"成功加载 {len(self.markets)} 个交易对")
        except Exception as e:
            logger.error(f"加载市场数据失败: {e}")
            raise Exception(f"Failed to load markets: {str(e)}")
    
    def _amount_to_precision(self, symbol: str, amount: float) -> float:
        """转换数量到交易所精度要求"""
        try:
            result = self.exchange.amount_to_precision(symbol, amount)
            return float(result)
        except Exception as e:
            raise Exception(f"Failed to format amount precision: {str(e)}")
    
    def _price_to_precision(self, symbol: str, price: float) -> float:
        """转换价格到交易所精度要求"""
        try:
            result = self.exchange.price_to_precision(symbol, price)
            return float(result)
        except Exception as e:
            raise Exception(f"Failed to format price precision: {str(e)}")
    
    def get_current_price(self, symbol: str) -> float:
        """获取当前市场价格"""
        try:
            return float(self.markets[symbol]["info"]["midPx"])
        except Exception as e:
            raise Exception(f"Failed to get price for {symbol}: {str(e)}")
    
    # ========== 余额相关 ==========
    
    def get_balance(self) -> Dict[str, Any]:
        """获取账户余额（旧接口）"""
        return self.fetch_balance()
    
    def fetch_balance(self) -> Dict[str, Any]:
        """获取账户余额"""
        try:
            balance = self.exchange.fetch_balance()
            logger.info("成功获取账户余额")
            return balance
        except Exception as e:
            logger.error(f"获取余额失败: {e}")
            raise Exception(f"Failed to fetch balance: {str(e)}")
    
    # ========== 持仓相关 ==========
    
    def get_positions(self, symbols: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """获取持仓（旧接口）"""
        if symbols:
            return self.fetch_positions(symbols)
        else:
            try:
                positions = self.exchange.fetch_positions()
                return [pos for pos in positions if float(pos.get("contracts", 0)) != 0]
            except Exception as e:
                logger.error(f"获取持仓失败: {e}")
                raise
    
    def fetch_positions(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """获取指定交易对的持仓"""
        try:
            positions = self.exchange.fetch_positions(symbols)
            return [pos for pos in positions if float(pos["contracts"]) != 0]
        except Exception as e:
            raise Exception(f"Failed to fetch positions: {str(e)}")
    
    # ========== 行情相关 ==========
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """获取交易对行情"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            logger.info(f"获取 {symbol} 行情成功")
            return ticker
        except Exception as e:
            logger.error(f"获取 {symbol} 行情失败: {e}")
            raise
    
    def fetch_ohlcv(self, symbol: str, timeframe: str = "1d", limit: int = 100) -> pd.DataFrame:
        """获取 K 线数据"""
        try:
            ohlcv_data = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            df = pd.DataFrame(
                data=ohlcv_data,
                columns=["timestamp", "open", "high", "low", "close", "volume"]
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df = df.set_index("timestamp").sort_index()
            
            numeric_cols = ["open", "high", "low", "close", "volume"]
            df[numeric_cols] = df[numeric_cols].astype(float)
            
            return df
        except Exception as e:
            raise Exception(f"Failed to fetch OHLCV data: {str(e)}")
    
    # ========== 订单相关 ==========
    
    def create_market_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        reduce_only: bool = False
    ) -> Dict[str, Any]:
        """创建市价单（旧接口）"""
        return self.place_market_order(symbol, side, amount, reduce_only)
    
    def place_market_order(
        self, 
        symbol: str, 
        side: str, 
        amount: float,
        reduce_only: bool = False,
        take_profit_price: Optional[float] = None,
        stop_loss_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """下市价单"""
        try:
            formatted_amount = self._amount_to_precision(symbol, amount)
            price = float(self.markets[symbol]["info"]["midPx"])
            formatted_price = self._price_to_precision(symbol, price)
            
            params = {"reduceOnly": reduce_only}
            
            if take_profit_price is not None:
                formatted_tp_price = self._price_to_precision(symbol, take_profit_price)
                params["takeProfitPrice"] = formatted_tp_price
                
            if stop_loss_price is not None:
                formatted_sl_price = self._price_to_precision(symbol, stop_loss_price)
                params["stopLossPrice"] = formatted_sl_price
            
            order = self.exchange.create_order(
                symbol=symbol,
                type="market",
                side=side,
                amount=formatted_amount,
                price=formatted_price,
                params=params
            )
            
            logger.info(f"市价单创建成功: {symbol} {side} {amount}")
            return order
        except Exception as e:
            logger.error(f"创建市价单失败: {e}")
            raise Exception(f"Failed to place market order: {str(e)}")
    
    def create_limit_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        price: float,
        reduce_only: bool = False
    ) -> Dict[str, Any]:
        """创建限价单"""
        try:
            formatted_amount = self._amount_to_precision(symbol, amount)
            formatted_price = self._price_to_precision(symbol, price)
            
            params = {"reduceOnly": reduce_only}
            
            order = self.exchange.create_order(
                symbol=symbol,
                type="limit",
                side=side,
                amount=formatted_amount,
                price=formatted_price,
                params=params
            )
            
            logger.info(f"限价单创建成功: {symbol} {side} {amount} @ {price}")
            return order
        except Exception as e:
            logger.error(f"创建限价单失败: {e}")
            raise
    
    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """取消订单"""
        try:
            result = self.exchange.cancel_order(order_id, symbol)
            logger.info(f"订单取消成功: {order_id}")
            return result
        except Exception as e:
            logger.error(f"取消订单失败: {e}")
            raise
    
    def get_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """查询订单状态"""
        try:
            order = self.exchange.fetch_order(order_id, symbol)
            logger.info(f"查询订单成功: {order_id}")
            return order
        except Exception as e:
            logger.error(f"查询订单失败: {e}")
            raise
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取未成交订单"""
        try:
            orders = self.exchange.fetch_open_orders(symbol)
            logger.info(f"获取未成交订单成功: {len(orders)} 个")
            return orders
        except Exception as e:
            logger.error(f"获取未成交订单失败: {e}")
            raise
    
    # ========== 杠杆和保证金 ==========
    
    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """设置杠杆"""
        try:
            self.exchange.set_leverage(leverage, symbol)
            logger.info(f"设置杠杆成功: {symbol} {leverage}x")
            return True
        except Exception as e:
            logger.error(f"设置杠杆失败: {e}")
            raise Exception(f"Failed to set leverage: {str(e)}")
    
    def set_margin_mode(self, symbol: str, margin_mode: str, leverage: int) -> bool:
        """设置保证金模式"""
        try:
            self.exchange.set_margin_mode(margin_mode, symbol, params={"leverage": leverage})
            logger.info(f"设置保证金模式成功: {symbol} {margin_mode}")
            return True
        except Exception as e:
            logger.error(f"设置保证金模式失败: {e}")
            raise Exception(f"Failed to set margin mode: {str(e)}")

