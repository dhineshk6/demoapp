import ccxt
import pandas as pd
import numpy as np
import ta
import time
import logging
import sys
from decimal import Decimal, InvalidOperation
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kucoin_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================== Strategy Classes ==================
class Strategy:
    def generate_signal(self, df: pd.DataFrame) -> str:
        raise NotImplementedError

class MeanReversionStrategy(Strategy):
    def generate_signal(self, df: pd.DataFrame) -> str:
        try:
            if len(df) < 20 or df['close'].isnull().any():
                return 'neutral'
            
            bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
            df['upper_band'] = bb.bollinger_hband()
            df['lower_band'] = bb.bollinger_lband()
            
            last_close = df['close'].iloc[-1]
            if last_close > df['upper_band'].iloc[-1]:
                return 'short'
            elif last_close < df['lower_band'].iloc[-1]:
                return 'long'
            return 'neutral'
        except Exception as e:
            logger.error(f"MeanReversion error: {str(e)}")
            return 'neutral'

class TrendFollowingStrategy(Strategy):
    def generate_signal(self, df: pd.DataFrame) -> str:
        try:
            if len(df) < 200 or df['close'].isnull().any():
                return 'neutral'
            
            ema50 = ta.trend.EMAIndicator(df['close'], window=50)
            ema200 = ta.trend.EMAIndicator(df['close'], window=200)
            adx = ta.trend.ADXIndicator(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=14
            )
            
            df['ema_50'] = ema50.ema_indicator()
            df['ema_200'] = ema200.ema_indicator()
            df['adx'] = adx.adx()
            
            last_ema50 = df['ema_50'].iloc[-1]
            last_ema200 = df['ema_200'].iloc[-1]
            last_adx = df['adx'].iloc[-1]
            
            if last_ema50 > last_ema200 and last_adx > 25:
                return 'long'
            elif last_ema50 < last_ema200 and last_adx > 25:
                return 'short'
            return 'neutral'
        except Exception as e:
            logger.error(f"TrendFollowing error: {str(e)}")
            return 'neutral'

# ================== Support Classes ==================
class DynamicRiskModel:
    def calculate_risk_score(self, market_data: Dict) -> float:
        try:
            volatility = max(market_data.get('volatility', 0.02), 0.01)
            liquidity = market_data.get('liquidity', 100)
            signals = market_data.get('signals', {})
            
            volatility_score = 1 / volatility
            liquidity_score = liquidity / 1000
            signal_score = (sum(1 for s in signals.values() if s == 'long') -
                          sum(1 for s in signals.values() if s == 'short')) / max(len(signals), 1)
            
            return min(0.5, (volatility_score + liquidity_score + signal_score) / 3)
        except Exception as e:
            logger.error(f"Risk calculation error: {str(e)}")
            return 0.1

class TradePerformanceTracker:
    def __init__(self):
        self.trade_history = []
    
    def log_trade(self, order: Dict):
        try:
            self.trade_history.append({
                'timestamp': pd.Timestamp.now(),
                'symbol': order.get('symbol', 'UNKNOWN'),
                'side': order.get('side', 'UNKNOWN'),
                'price': order.get('price', 0.0),
                'amount': order.get('amount', 0.0),
                'leverage': order.get('leverage', 1.0)
            })
        except Exception as e:
            logger.error(f"Trade logging failed: {str(e)}")

# ================== Main Trading Bot Class ==================
class KuCoinTradingBot:
    def __init__(self, api_key: str, api_secret: str, api_passphrase: str):
        self.exchange = self._initialize_exchange(api_key, api_secret, api_passphrase)
        self.strategies = [
            MeanReversionStrategy(),
            TrendFollowingStrategy()
        ]
        self.risk_model = DynamicRiskModel()
        self.performance_tracker = TradePerformanceTracker()
        self.min_volatility = 0.02
        self.max_leverage = 20
        self.min_data_length = 200
        self.initial_investment = None
        self.total_invested = 0.0

    def _initialize_exchange(self, api_key: str, api_secret: str, api_passphrase: str) -> ccxt.Exchange:
        exchange = ccxt.kucoinfutures({
            'apiKey': api_key,
            'secret': api_secret,
            'password': api_passphrase,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
                'adjustForTimeDifference': True
            }
        })
        
        for attempt in range(3):
            try:
                exchange.load_markets()
                logger.info(f"Successfully loaded {len(exchange.markets)} markets")
                return exchange
            except ccxt.AuthenticationError as e:
                logger.critical("Authentication failed! Check API credentials")
                raise SystemExit("Invalid API keys or passphrase")
            except Exception as e:
                logger.error(f"Market load failed (attempt {attempt+1}/3): {str(e)}")
                time.sleep(5)
        
        raise RuntimeError("Failed to initialize KuCoin exchange")

    def set_initial_investment(self):
        """Interactive prompt for initial investment amount"""
        while True:
            try:
                balance = self._get_available_balance()
                print(f"\nAvailable balance: {balance:.2f} USDT")
                amount = Decimal(input("Enter initial investment amount (USDT): "))
                
                if amount <= 0:
                    print("Amount must be positive")
                    continue
                    
                if amount > Decimal(str(balance)):
                    print(f"Amount exceeds available balance. Max: {balance:.2f}")
                    continue
                    
                self.initial_investment = float(amount)
                self.total_invested = self.initial_investment
                logger.info(f"Initial investment set to: {self.initial_investment:.2f} USDT")
                break
                
            except InvalidOperation:
                print("Invalid input. Please enter a valid number")
            except Exception as e:
                logger.error(f"Investment error: {str(e)}")
                raise

    def analyze_market(self, symbols: List[str]) -> Dict:
        market_data = {}
        for symbol in symbols:
            try:
                if ":USDT" not in symbol:
                    continue
                
                df = self.fetch_market_data(symbol)
                if df.empty or len(df) < self.min_data_length:
                    continue
                
                df = self.calculate_metrics(df)
                signals = {
                    strategy.__class__.__name__: strategy.generate_signal(df)
                    for strategy in self.strategies
                }
                
                market_data[symbol] = {
                    'signals': signals,
                    'volatility': self._calculate_volatility(df),
                    'liquidity': self._assess_liquidity(symbol),
                    'price': df['close'].iloc[-1]
                }
            except Exception as e:
                logger.error(f"Analysis failed for {symbol}: {str(e)}")
        return market_data

    def fetch_market_data(self, symbol: str, timeframe: str = '5m', limit: int = 500) -> pd.DataFrame:
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            if len(ohlcv) < self.min_data_length:
                return pd.DataFrame()
                
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df.dropna()
        except Exception as e:
            logger.error(f"Data fetch failed for {symbol}: {str(e)}")
            return pd.DataFrame()

    def calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df['atr'] = ta.volatility.average_true_range(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=14
            )
            df['rsi'] = ta.momentum.rsi(df['close'], window=14)
            return df.dropna()
        except Exception as e:
            logger.error(f"Metric calculation failed: {str(e)}")
            return pd.DataFrame()

    def _calculate_volatility(self, df: pd.DataFrame) -> float:
        try:
            return df['atr'].iloc[-1] / df['close'].iloc[-1]
        except Exception as e:
            logger.error(f"Volatility calculation failed: {str(e)}")
            return 0.0

    def _assess_liquidity(self, symbol: str) -> float:
        try:
            order_book = self.exchange.fetch_order_book(symbol)
            best_ask = order_book['asks'][0][0] if order_book['asks'] else 0
            best_bid = order_book['bids'][0][0] if order_book['bids'] else 0
            spread = best_ask - best_bid
            return 1 / spread if spread > 0 else 0
        except Exception as e:
            logger.error(f"Liquidity check failed for {symbol}: {str(e)}")
            return 0

    def execute_trades(self, market_analysis: Dict):
        try:
            if self.initial_investment is None:
                logger.error("Initial investment not set!")
                return

            balance = self._get_available_balance()
            if balance <= 0:
                logger.warning("Insufficient balance for trading")
                return
                
            portfolio = []
            
            for symbol, data in market_analysis.items():
                try:
                    if data['liquidity'] < 100:
                        logger.debug(f"Skipping {symbol} - Low liquidity: {data['liquidity']:.2f}")
                        continue
                        
                    if data['volatility'] < self.min_volatility:
                        logger.debug(f"Skipping {symbol} - Low volatility: {data['volatility']:.4f}")
                        continue

                    risk_score = self.risk_model.calculate_risk_score(data)
                    leverage = min(self.max_leverage, int(1 / max(data['volatility'], 0.01)))
                    position_size = min(self.initial_investment * risk_score, balance * 0.1)

                    logger.info(
                        f"{symbol} | "
                        f"Price: {data['price']:.4f} | "
                        f"Volatility: {data['volatility']:.4f} | "
                        f"Risk Score: {risk_score:.2f} | "
                        f"Position Size: {position_size:.2f}"
                    )

                    if position_size >= 10:
                        direction = self._determine_direction(data['signals'])
                        portfolio.append({
                            'symbol': symbol,
                            'direction': direction,
                            'size': round(position_size, 2),
                            'leverage': leverage,
                            'price': data['price']
                        })

                except Exception as e:
                    logger.error(f"Trade setup failed for {symbol}: {str(e)}")

            portfolio.sort(key=lambda x: x['size'] / max(x['price'] * x['leverage'], 1), reverse=True)
            
            if portfolio:
                logger.info(f"Executing {len(portfolio[:3])} trades")
                for trade in portfolio[:3]:
                    self._execute_trade(trade)
                    self.total_invested += trade['size']
                    logger.info(f"Executed {trade['direction']} order for {trade['symbol']} | "
                               f"Size: {trade['size']:.2f} USDT | "
                               f"Leverage: {trade['leverage']}x")
            else:
                logger.info("No valid trades found this cycle")

        except Exception as e:
            logger.error(f"Trade execution failed: {str(e)}")

    def _get_available_balance(self) -> float:
        try:
            balance = self.exchange.fetch_balance(params={'type': 'future'})
            return balance['USDT']['free']
        except ccxt.AuthenticationError as e:
            logger.critical("Authentication failed! Check API credentials")
            raise SystemExit("Invalid API keys or passphrase")
        except Exception as e:
            logger.error(f"Balance check failed: {str(e)}")
            return 0

    def _determine_direction(self, signals: Dict) -> str:
        long_count = sum(1 for s in signals.values() if s == 'long')
        short_count = sum(1 for s in signals.values() if s == 'short')
        return 'long' if long_count > short_count else 'short'

    def _execute_trade(self, trade: Dict):
        try:
            self.exchange.set_leverage(trade['leverage'], trade['symbol'])
            
            amount = trade['size'] / trade['price'] * trade['leverage']
            amount = self.exchange.amount_to_precision(trade['symbol'], amount)
            
            order = self.exchange.create_market_order(
                trade['symbol'],
                trade['direction'],
                amount,
                params={'leverage': trade['leverage']}
            )
            
            self._place_risk_orders(trade, order)
            self.performance_tracker.log_trade(order)
            
        except Exception as e:
            logger.error(f"Trade failed for {trade['symbol']}: {str(e)}")

    def _place_risk_orders(self, trade: Dict, main_order: Dict):
        try:
            price = trade['price']
            atr = trade['size'] * trade['volatility']
            
            if trade['direction'] == 'long':
                stop_loss = price - (2 * atr)
                take_profit = price + (3 * atr)
                stop_side = 'sell'
            else:
                stop_loss = price + (2 * atr)
                take_profit = price - (3 * atr)
                stop_side = 'buy'

            self.exchange.create_order(
                symbol=trade['symbol'],
                type='STOP',
                side=stop_side,
                amount=main_order['amount'],
                stopPrice=stop_loss,
                params={'reduceOnly': True}
            )
            
            self.exchange.create_order(
                symbol=trade['symbol'],
                type='LIMIT',
                side=stop_side,
                amount=main_order['amount'],
                price=take_profit,
                params={'reduceOnly': True}
            )
        except Exception as e:
            logger.error(f"Risk orders failed for {trade['symbol']}: {str(e)}")

if __name__ == "__main__":
    API_KEY = ""
    API_SECRET = ""
    API_PASSPHRASE = ""
    
    MAX_RETRIES = 5
    RETRY_DELAY = 300  # 5 minutes
    
    retry_count = 0
    
    while retry_count < MAX_RETRIES:
        try:
            bot = KuCoinTradingBot(
                api_key=API_KEY,
                api_secret=API_SECRET,
                api_passphrase=API_PASSPHRASE
            )
            
            # Set initial investment interactively
            bot.set_initial_investment()
            
            symbols = [s for s in bot.exchange.markets.keys() if ":USDT" in s][:50]
            logger.info(f"Monitoring {len(symbols)} symbols")
            
            while True:
                try:
                    logger.info("Starting analysis cycle...")
                    market_data = bot.analyze_market(symbols)
                    logger.info(f"Found {len(market_data)} tradable symbols")
                    
                    logger.info("Executing trades...")
                    bot.execute_trades(market_data)
                    
                    logger.info(f"Cycle completed. Sleeping for {RETRY_DELAY//60} minutes")
                    time.sleep(RETRY_DELAY)
                    
                except ccxt.NetworkError as e:
                    logger.warning(f"Network error: {str(e)}")
                    time.sleep(60)
                    
                except KeyboardInterrupt:
                    logger.info("Bot stopped by user")
                    sys.exit(0)
                    
                except Exception as e:
                    logger.error(f"Unexpected error: {str(e)}")
                    retry_count += 1
                    if retry_count >= MAX_RETRIES:
                        logger.critical("Max retries reached")
                        sys.exit(1)
                    time.sleep(300)
        
        except ccxt.AuthenticationError as e:
            logger.critical("Authentication failed! Check API credentials")
            sys.exit(1)
            
        except Exception as e:
            logger.critical(f"Initialization failed: {str(e)}")
            retry_count += 1
            time.sleep(60 * retry_count)
    
    logger.critical("Permanent failure after multiple retries")
    sys.exit(1)
