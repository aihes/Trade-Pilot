"""
Hyperliquid 官方 SDK 客户端封装

这个客户端使用 Hyperliquid 官方的 Python SDK (hyperliquid-python-sdk)
提供与 CCXT 客户端类似的接口，但使用官方 SDK 的原生功能。

官方 SDK 文档: https://github.com/hyperliquid-dex/hyperliquid-python-sdk
"""

from typing import Optional, Dict, List, Any
import pandas as pd
import eth_account
from eth_account.signers.local import LocalAccount
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants


class HyperliquidSDKClient:
    """
    Hyperliquid 官方 SDK 客户端
    
    使用官方 hyperliquid-python-sdk 库进行交易和数据查询
    
    认证方式:
    1. 主钱包认证: wallet_address + private_key
    2. API Wallet 认证: wallet_address + api_wallet_private_key + vault_address
    3. 只读模式: read_only=True (无需认证)
    
    示例:
        # 主钱包认证
        client = HyperliquidSDKClient(
            wallet_address="0x...",
            private_key="..."
        )
        
        # API Wallet 认证
        client = HyperliquidSDKClient(
            wallet_address="0x...",
            private_key="api_wallet_key",
            vault_address="0x..."
        )
        
        # 只读模式
        client = HyperliquidSDKClient(read_only=True)
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
        初始化 Hyperliquid 官方 SDK 客户端
        
        Args:
            wallet_address: 钱包地址（主钱包地址）
            private_key: 私钥（主钱包私钥或 API Wallet 私钥）
            vault_address: Vault 地址（用于 API Wallet 代理子账户）
            testnet: 是否使用测试网
            read_only: 是否只读模式（无需认证）
            custom_endpoint: 自定义 API endpoint
        """
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.vault_address = vault_address
        self.testnet = testnet
        self.read_only = read_only
        
        # 确定 API URL
        if custom_endpoint:
            self.api_url = custom_endpoint
        elif testnet:
            self.api_url = constants.TESTNET_API_URL
        else:
            self.api_url = constants.MAINNET_API_URL
        
        # 验证认证参数
        if not read_only:
            if not wallet_address or not private_key:
                raise ValueError(
                    "必须提供以下认证方式之一：\n"
                    "1. wallet_address + private_key（钱包认证）\n"
                    "   - 主钱包模式：HyperliquidSDKClient(wallet_address='0x...', private_key='...')\n"
                    "   - API Wallet 模式：HyperliquidSDKClient(wallet_address='0x...', private_key='...', vault_address='0x...')\n"
                    "2. read_only=True（只读模式）\n"
                    "\n"
                    "注意：Hyperliquid 不支持传统的 API Key + Secret 认证！\n"
                    "如需使用 API Wallet，请访问 https://app.hyperliquid.xyz/API 生成并授权。"
                )
        
        # 初始化 Info 客户端（用于查询数据）
        self.info = Info(self.api_url, skip_ws=True)

        # 初始化 Exchange 客户端（用于交易）
        self.exchange = None
        self.account = None
        if not read_only and wallet_address and private_key:
            # 从私钥创建 LocalAccount 对象
            self.account: LocalAccount = eth_account.Account.from_key(private_key)

            # 创建 Exchange 实例
            # 如果提供了 vault_address，则使用 account_address 参数指定主钱包地址
            self.exchange = Exchange(
                self.account,
                base_url=self.api_url,
                account_address=wallet_address if vault_address else None
            )
        
        # 设置认证方式标识
        if read_only:
            self.auth_method = "read_only"
        elif vault_address:
            self.auth_method = "api_wallet"
        else:
            self.auth_method = "main_wallet"
        
        # 加载市场数据
        self.markets = self._load_markets()
    
    def _load_markets(self) -> Dict[str, Any]:
        """加载市场数据"""
        try:
            meta = self.info.meta()
            markets = {}
            
            if meta and 'universe' in meta:
                for asset in meta['universe']:
                    symbol = asset['name']
                    markets[symbol] = {
                        'symbol': symbol,
                        'name': asset.get('name'),
                        'szDecimals': asset.get('szDecimals', 0),
                    }
            
            return markets
        except Exception as e:
            print(f"加载市场数据失败: {e}")
            return {}
    
    def get_current_price(self, symbol: str) -> float:
        """
        获取当前价格
        
        Args:
            symbol: 交易对符号，例如 "BTC" 或 "ETH"
            
        Returns:
            当前价格
        """
        try:
            # 移除 /USDC:USDC 后缀，只保留基础符号
            base_symbol = symbol.split('/')[0] if '/' in symbol else symbol
            
            # 获取所有价格
            all_mids = self.info.all_mids()
            
            if base_symbol in all_mids:
                return float(all_mids[base_symbol])
            else:
                raise ValueError(f"未找到交易对: {symbol}")
        except Exception as e:
            raise Exception(f"获取价格失败: {e}")
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        获取行情数据
        
        Args:
            symbol: 交易对符号
            
        Returns:
            行情数据字典
        """
        try:
            base_symbol = symbol.split('/')[0] if '/' in symbol else symbol
            
            # 获取用户状态（包含持仓和余额信息）
            if self.wallet_address:
                user_state = self.info.user_state(self.wallet_address)
            else:
                user_state = None
            
            # 获取价格
            price = self.get_current_price(base_symbol)
            
            return {
                'symbol': symbol,
                'last': price,
                'bid': price,  # 官方 SDK 没有直接的 bid/ask，使用 mid price
                'ask': price,
                'timestamp': None,
                'datetime': None,
            }
        except Exception as e:
            raise Exception(f"获取行情失败: {e}")
    
    def fetch_balance(self) -> Dict[str, Any]:
        """
        获取账户余额
        
        Returns:
            余额信息字典
        """
        if self.read_only:
            raise Exception("只读模式无法获取余额")
        
        if not self.wallet_address:
            raise Exception("需要提供钱包地址")
        
        try:
            user_state = self.info.user_state(self.wallet_address)
            
            if not user_state:
                return {'free': {}, 'used': {}, 'total': {}}
            
            # 解析余额信息
            balance_info = {
                'free': {},
                'used': {},
                'total': {}
            }
            
            # 从 marginSummary 获取余额
            if 'marginSummary' in user_state:
                margin = user_state['marginSummary']
                total_value = float(margin.get('accountValue', 0))
                balance_info['total']['USDC'] = total_value
                balance_info['free']['USDC'] = total_value
            
            return balance_info
        except Exception as e:
            raise Exception(f"获取余额失败: {e}")
    
    def fetch_positions(self, symbols: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        获取持仓信息
        
        Args:
            symbols: 交易对列表（可选）
            
        Returns:
            持仓信息列表
        """
        if self.read_only:
            raise Exception("只读模式无法获取持仓")
        
        if not self.wallet_address:
            raise Exception("需要提供钱包地址")
        
        try:
            user_state = self.info.user_state(self.wallet_address)
            
            if not user_state or 'assetPositions' not in user_state:
                return []
            
            positions = []
            for pos in user_state['assetPositions']:
                position_info = pos.get('position', {})
                
                # 跳过没有持仓的
                if float(position_info.get('szi', 0)) == 0:
                    continue
                
                symbol = position_info.get('coin', '')
                size = float(position_info.get('szi', 0))
                entry_price = float(position_info.get('entryPx', 0))
                
                positions.append({
                    'symbol': symbol,
                    'side': 'long' if size > 0 else 'short',
                    'size': abs(size),
                    'entry_price': entry_price,
                    'unrealized_pnl': float(position_info.get('unrealizedPnl', 0)),
                    'leverage': float(position_info.get('leverage', {}).get('value', 1)),
                })
            
            # 如果指定了 symbols，过滤结果
            if symbols:
                base_symbols = [s.split('/')[0] if '/' in s else s for s in symbols]
                positions = [p for p in positions if p['symbol'] in base_symbols]
            
            return positions
        except Exception as e:
            raise Exception(f"获取持仓失败: {e}")
    
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100
    ) -> pd.DataFrame:
        """
        获取 K 线数据

        Args:
            symbol: 交易对符号
            timeframe: 时间周期 (1m, 5m, 15m, 1h, 4h, 1d)
            limit: 返回的 K 线数量

        Returns:
            包含 OHLCV 数据的 DataFrame
        """
        try:
            base_symbol = symbol.split('/')[0] if '/' in symbol else symbol

            # 将时间周期转换为官方 SDK 格式
            interval_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '1h': '1h',
                '4h': '4h',
                '1d': '1d',
            }

            interval = interval_map.get(timeframe, '1h')

            # 计算时间范围（获取最近的数据）
            import time
            end_time = int(time.time() * 1000)  # 当前时间（毫秒）
            # 根据时间周期计算开始时间
            interval_ms = {
                '1m': 60 * 1000,
                '5m': 5 * 60 * 1000,
                '15m': 15 * 60 * 1000,
                '1h': 60 * 60 * 1000,
                '4h': 4 * 60 * 60 * 1000,
                '1d': 24 * 60 * 60 * 1000,
            }
            start_time = end_time - (limit * interval_ms.get(timeframe, 60 * 60 * 1000))

            # 获取 K 线数据
            candles = self.info.candles_snapshot(
                name=base_symbol,  # 参数名是 name 而不是 coin
                interval=interval,
                startTime=start_time,
                endTime=end_time
            )
            
            if not candles:
                return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # 转换为 DataFrame
            df = pd.DataFrame(candles)
            
            # 重命名列
            df = df.rename(columns={
                't': 'timestamp',
                'o': 'open',
                'h': 'high',
                'l': 'low',
                'c': 'close',
                'v': 'volume'
            })
            
            # 转换数据类型
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 限制返回数量
            if len(df) > limit:
                df = df.tail(limit)
            
            return df.reset_index(drop=True)
        except Exception as e:
            raise Exception(f"获取 K 线数据失败: {e}")

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取未成交订单

        Args:
            symbol: 交易对符号（可选），例如 "BTC" 或 "BTC/USDC:USDC"

        Returns:
            未成交订单列表
        """
        if self.read_only:
            raise Exception("只读模式无法获取订单")

        if not self.wallet_address:
            raise Exception("需要提供钱包地址")

        try:
            user_state = self.info.user_state(self.wallet_address)

            if not user_state or 'openOrders' not in user_state:
                return []

            orders = []
            for order in user_state['openOrders']:
                order_symbol = order.get('coin', '')

                # 如果指定了 symbol，过滤结果
                if symbol:
                    base_symbol = symbol.split('/')[0] if '/' in symbol else symbol
                    if order_symbol != base_symbol:
                        continue

                orders.append({
                    'id': order.get('oid', ''),
                    'symbol': order_symbol,
                    'side': order.get('side', '').lower(),
                    'type': order.get('orderType', ''),
                    'price': float(order.get('limitPx', 0)),
                    'amount': float(order.get('sz', 0)),
                    'filled': float(order.get('sz', 0)) - float(order.get('szLeft', 0)),
                    'remaining': float(order.get('szLeft', 0)),
                    'timestamp': order.get('timestamp', 0),
                })

            return orders
        except Exception as e:
            raise Exception(f"获取未成交订单失败: {e}")

    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"HyperliquidSDKClient("
            f"auth_method={self.auth_method}, "
            f"testnet={self.testnet}, "
            f"markets={len(self.markets)})"
        )

