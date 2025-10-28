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

    支持两种认证方式：
    1. 钱包地址 + 私钥（推荐，用于交易）
       - 主钱包认证：使用主钱包地址和私钥
       - API Wallet 认证：使用 API Wallet 私钥 + vault_address 参数
    2. 只读模式（不需要认证，仅查询公开数据）

    注意：Hyperliquid 不支持传统的 API Key + Secret 认证方式！
    如需使用 API Wallet，请在 https://app.hyperliquid.xyz/API 生成并授权。
    """

    def __init__(
        self,
        wallet_address: Optional[str] = None,
        private_key: Optional[str] = None,
        vault_address: Optional[str] = None,
        testnet: bool = False,
        read_only: bool = False,
        custom_endpoint: Optional[str] = None
    ):
        """
        初始化 Hyperliquid 客户端

        Args:
            wallet_address: 钱包地址
                - 主钱包模式：主钱包地址
                - API Wallet 模式：主钱包地址（配合 vault_address 使用）
            private_key: 私钥
                - 主钱包模式：主钱包私钥
                - API Wallet 模式：API Wallet 私钥
            vault_address: Vault 地址（可选）
                - 用于 API Wallet 代理子账户或 Vault 进行交易
                - 如果不指定，默认使用 wallet_address
            testnet: 是否使用测试网（自动设置为 https://api.hyperliquid-testnet.xyz）
            read_only: 只读模式（不需要认证，仅查询公开数据）
            custom_endpoint: 自定义 API endpoint（可选，会覆盖 testnet 设置）

        认证方式：
        1. 主钱包认证（推荐）：
           HyperliquidClient(wallet_address="0x...", private_key="...")

        2. API Wallet 认证（用于子账户/Vault）：
           HyperliquidClient(
               wallet_address="0x...",  # 主钱包地址
               private_key="...",        # API Wallet 私钥
               vault_address="0x..."     # 子账户或 Vault 地址
           )

        3. 只读模式：
           HyperliquidClient(read_only=True)

        Endpoint 设置：
        - 主网（默认）: https://api.hyperliquid.xyz
        - 测试网（testnet=True）: https://api.hyperliquid-testnet.xyz
        - 自定义（custom_endpoint）: 使用指定的 URL

        测试网充值说明：
        - 必须先在主网用同一地址存入过资金
        - 访问 https://app.hyperliquid-testnet.xyz/drip 领取测试币
        - 每次可领取 1,000 mock USDC
        """
        self.testnet = testnet
        self.read_only = read_only
        self.custom_endpoint = custom_endpoint
        self.vault_address = vault_address

        # 确定使用的 endpoint
        if custom_endpoint:
            endpoint_url = custom_endpoint
            logger.info(f"使用自定义 endpoint: {endpoint_url}")
        elif testnet:
            endpoint_url = "https://api.hyperliquid-testnet.xyz"
            logger.info(f"使用测试网 endpoint: {endpoint_url}")
        else:
            endpoint_url = "https://api.hyperliquid.xyz"
            logger.info(f"使用主网 endpoint: {endpoint_url}")

        # 方式 1: 钱包地址 + 私钥（推荐用于交易）
        if wallet_address and private_key:
            if vault_address:
                logger.info(f"使用 API Wallet 认证（代理账户: {vault_address[:10]}...）")
            else:
                logger.info("使用主钱包认证")

            config = {
                "walletAddress": wallet_address,
                "privateKey": private_key,
                "enableRateLimit": True,
            }

            # 如果指定了 vault_address，添加到配置中
            if vault_address:
                config["vaultAddress"] = vault_address

            # 设置自定义 endpoint
            if custom_endpoint or testnet:
                config['urls'] = {
                    'api': {
                        'public': endpoint_url,
                        'private': endpoint_url,
                    }
                }
            self.exchange = ccxt.hyperliquid(config)
            self.auth_method = "wallet"
            self.wallet_address = wallet_address  # 保存钱包地址以备后用

        # 方式 2: 只读模式（不需要认证）
        elif read_only:
            if wallet_address:
                logger.info(f"使用只读模式（查询钱包: {wallet_address[:10]}...）")
                config = {
                    'walletAddress': wallet_address,
                    'enableRateLimit': True,
                }
            else:
                logger.info("使用只读模式（无认证）")
                config = {
                    'enableRateLimit': True,
                }
            
            # 设置自定义 endpoint
            if custom_endpoint or testnet:
                config['urls'] = {
                    'api': {
                        'public': endpoint_url,
                        'private': endpoint_url,
                    }
                }
            self.exchange = ccxt.hyperliquid(config)
            self.auth_method = "read_only"
            self.wallet_address = wallet_address  # 保存钱包地址以备后用

        else:
            raise ValueError(
                "必须提供以下认证方式之一：\n"
                "1. wallet_address + private_key（钱包认证）\n"
                "   - 主钱包模式：HyperliquidClient(wallet_address='0x...', private_key='...')\n"
                "   - API Wallet 模式：HyperliquidClient(wallet_address='0x...', private_key='...', vault_address='0x...')\n"
                "2. read_only=True（只读模式）\n"
                "\n"
                "注意：Hyperliquid 不支持传统的 API Key + Secret 认证！\n"
                "如需使用 API Wallet，请访问 https://app.hyperliquid.xyz/API 生成并授权。"
            )

        # 加载市场数据
        self.markets = {}
        self._load_markets()

        logger.info(f"Hyperliquid 客户端初始化完成 (认证方式={self.auth_method}, endpoint={endpoint_url})")
    
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
        # 检查是否在只读模式下且未提供钱包地址
        if self.auth_method == "read_only" and not self.wallet_address:
            raise Exception(
                "获取余额失败: 在只读模式下查询余额需要提供钱包地址。\n"
                "请在初始化时提供 wallet_address 参数（无需私钥）。\n"
                "示例: HyperliquidClient(wallet_address='0x...', read_only=True)"
            )
        
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

