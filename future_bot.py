import ccxt
import sqlite3
import time
# import talib  # <-- talib import still here, we'll remove later if switching to pandas-ta
import numpy as np
import pandas as pd
import pandas_ta as pta

# --- CONFIGURATION ---

KUCOIN_API_KEY = " "
KUCOIN_API_SECRET = ""
KUCOIN_API_PASSPHRASE = ""  # If applicable

DATABASE_NAME = "crypto_trading_bot_single.db"

# Risk Management Parameters (Example - adjust these carefully)
RISK_PER_TRADE_PERCENT = 0.01  # 1% risk of account balance per trade
MAX_DRAWDOWN_PERCENT = 0.10  # 10% maximum drawdown before stopping (example)
LEVERAGE = 3  # Example Leverage - be extremely cautious with high leverage
INITIAL_BALANCE = None # Will be fetched and set dynamically

# Trading Strategy Parameters (Example - RSI Strategy with SMA & MACD Confirmation)
RSI_OVERBOUGHT = 60  # Changed from 70 to 60 - making it more sensitive
RSI_OVERSOLD = 40   # Changed from 30 to 40 - making it more sensitive
RSI_PERIOD = 14
SMA_PERIOD = 10  # Changed from 20 to 10 - making SMA faster
# MACD Parameters (using default periods: Fast MA 12, Slow MA 26, Signal MA 9)
MACD_FAST_PERIOD = 12  # Default Fast EMA period for MACD
MACD_SLOW_PERIOD = 26  # Default Slow EMA period for MACD
MACD_SIGNAL_PERIOD = 9 # Default Signal EMA period for MACD


# Trading Symbols to Monitor (Example - adjust as needed)
TRADE_SYMBOLS = ["BTC/USDT:USDT", "ETH/USDT:USDT"]  # UPDATED to correct symbols

# Order Size Parameters
MIN_ORDER_NOTIONAL = 5  # Minimum order value in USDT (KuCoin Futures min order)

# --- CCXT KUCOIN FUTURES API CLIENT --- #  <---  NEW API CLIENT USING CCXT
class CcxtKucoinAPIClient:
    def __init__(self):
        try:
            self.exchange = ccxt.kucoinfutures({ # Instantiate ccxt KuCoin Futures exchange
                'apiKey': KUCOIN_API_KEY,
                'secret': KUCOIN_API_SECRET,
                'password': KUCOIN_API_PASSPHRASE,
            })
            self.exchange.verbose = True # <-- ENABLE VERBOSE MODE for detailed ccxt logs
            print("CcxtKucoinAPIClient initialized via ccxt (verbose mode ON)") # Success message with verbose indication
        except Exception as e: # Catch initialization errors
            print(f"Error initializing CcxtKucoinAPIClient: {e}")
            raise


    def get_active_trade_symbols(self):
        """Fetches active futures trading symbols using ccxt with detailed debug."""
        print("\n--- get_active_trade_symbols() START ---") # Debug: Function start
        try:
            print("Fetching markets via exchange.load_markets(params={'reload': True})...") # Debug: Before load_markets
            markets = self.exchange.load_markets(params={'reload': True}) # Force reload markets, debug parameter added
            print(f"Debug: exchange.load_markets() call completed. Type of 'markets' is: {type(markets)}") # Debug: Type of 'markets'

            if not markets:
                print("Warning: exchange.load_markets() returned an empty 'markets' object.") # Debug: Empty markets check
                return []

            print(f"Debug: Total markets fetched from exchange.load_markets(): {len(markets)}") # Debug: Total markets count

            print("\n--- Raw 'markets' data (first 20 items): ---") # Debug: Raw markets data
            count = 0
            for market_key, market_value in markets.items(): # Iterate through markets.items()
                print(f"Market Key: {market_key}, Market Value: {market_value}") # Print each market item
                count += 1
                if count >= 20: # Limit to first 20 for brevity in output (can remove limit for full output if needed)
                    print("... (Output truncated after first 20 markets for brevity) ...")
                    break

            active_symbols = []
            print("\n--- Filtering markets for active futures ---") # Debug: Filtering start
            for symbol, market in markets.items():
                try: # Add try-except inside loop for robustness
                    if market and market['active'] and market['type'] == 'future': # Check if market is valid before accessing keys
                        active_symbols.append(symbol)
                        print(f"Debug: Added symbol '{symbol}', type: '{market['type']}', active: {market['active']}") # Debug: Symbol addition
                    else:
                        print(f"Debug: Skipped symbol '{symbol}', market info: {market}") # Debug: Skipped symbol reason
                except Exception as loop_e: # Catch errors within the loop itself
                    print(f"Error processing market '{symbol}' in loop: {loop_e}") # Log errors in loop

            print(f"Debug: Number of active futures symbols after filtering: {len(active_symbols)}") # Debug: Active symbols count
            print("--- get_active_trade_symbols() END ---\n") # Debug: Function end
            return active_symbols

        except ccxt.RateLimitExceeded as e: # Catch rate limit errors specifically
            print(f"CCXT Rate Limit Exceeded Error in get_active_trade_symbols(): {e}")
            print("--- get_active_trade_symbols() END (Rate Limit Error) ---\n") # Debug: Function end (error)
            return []
        except ccxt.NetworkError as e: # Catch network connection errors
            print(f"CCXT Network Error in get_active_trade_symbols(): {e}")
            print("--- get_active_trade_symbols() END (Network Error) ---\n") # Debug: Function end (error)
            return []
        except Exception as e: # Catch any other errors
            print(f"General Error in get_active_trade_symbols(): {e}") # More general error log
            print(f"Error details: {e}") # Print exception details
            print("--- get_active_trade_symbols() END (General Error) ---\n") # Debug: Function end (error)
            return []


    def print_active_symbols(self): # <-- ADDED FUNCTION TO PRINT ACTIVE SYMBOLS
        """Prints active futures symbols from the exchange."""
        active_symbols = self.get_active_trade_symbols()
        if active_symbols:
            print(f"\nActive Futures Symbols on KuCoin Futures (ccxt): (Count: {len(active_symbols)})") # Print count of symbols
            for symbol in sorted(active_symbols): # Print symbols alphabetically for easier reading
                print(f"- {symbol}")
        else:
            print("Could not fetch active futures symbols.")


    def get_historical_data(self, symbol, timeframe, since, limit=None):
        """Fetches historical kline data for a symbol using ccxt."""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
            return [{'timestamp': int(k[0]), 'open': float(k[1]), 'high': float(k[2]), 'low': float(k[3]), 'close': float(k[4]), 'volume': float(k[5])} for k in ohlcv] # Format to match historical_data table
        except Exception as e:
            print(f"Error fetching historical data for {symbol} via ccxt: {e}")
            return None

    def get_ticker(self, symbol):
        """Fetches the latest ticker data for a symbol using ccxt."""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            print(f"Error fetching ticker data for {symbol} via ccxt: {e}")
            return None

    def get_account_balance(self, currency='USDT'):
        """Fetches futures account balance for a specific currency using ccxt."""
        try:
            balance_data = self.exchange.fetch_balance({'type': 'future'}) # Use ccxt's fetch_balance with type='future'
            if currency in balance_data and 'total' in balance_data[currency]: # Check if currency and 'total' key exist
                return float(balance_data[currency]['total']) # Return total balance in specified currency
            else:
                print(f"Currency {currency} not found in balance data or 'total' balance missing in ccxt response.")
                return 0.0 # Currency balance not found or invalid data
        except Exception as e:
            print(f"Error fetching account balance via ccxt: {e}")
            return None


    def place_order(self, symbol, side, order_type, size, price=None):
        """Places a futures order using ccxt."""
        try:
            order = self.exchange.create_order(
                symbol,
                order_type.upper(), # ccxt order type needs to be uppercase
                side.upper(),      # ccxt side needs to be uppercase
                size,
                price,
                params={'leverage': LEVERAGE} # Pass leverage as params
            )
            return order
        except Exception as e:
            print(f"Error placing order for {symbol} {side} {order_type} via ccxt: {e}")
            return None

    def get_position(self, symbol):
        """Gets current position details for a symbol using ccxt (modified for symbol filtering)."""
        try:
            positions = self.exchange.fetch_positions() # Fetch ALL positions (no symbol argument)
            if positions:
                for position in positions: # Iterate through ALL positions fetched
                    if position['symbol'] == symbol and position['contracts'] != 0: # Find the one matching our symbol and with contracts
                        return position
            return None # No position found for this symbol
        except Exception as e:
            print(f"Error getting position for {symbol} via ccxt: {e}")
            return None

    def close_position(self, symbol, side):
        """Closes an existing position (market close) using ccxt."""
        try:
            position = self.get_position(symbol)
            if position:
                close_size = abs(position['contracts']) # Use abs to handle both long and short
                if side == 'long':
                    close_side = 'sell'
                elif side == 'short':
                    close_side = 'buy'
                else:
                    print(f"Invalid side for closing position: {side}")
                    return None

                order = self.place_order(symbol, close_side, 'market', close_size)
                return order
            else:
                print(f"No position to close for {symbol}")
                return None
        except Exception as e:  # <---  ADDED EXCEPT BLOCK HERE
            print(f"Error closing position for {symbol} via ccxt: {e}") # Error print if closing fails
            return None # Return None in case of error

    def cancel_all_orders(self, symbol):
        """Cancels all open orders for a symbol using ccxt (optional)."""
        try:
            self.exchange.cancel_all_orders(symbol)
            print(f"Cancelled all orders for {symbol} via ccxt")
        except Exception as e:
            print(f"Error cancelling orders for {symbol} via ccxt: {e}")


# --- DATABASE MANAGER --- (No changes needed for DatabaseManager)
class DatabaseManager:
    def __init__(self, db_name=DATABASE_NAME):
        self.db_name = db_name
        self.conn = None

    def connect(self):
        """Connect to the database."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            return self.conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return None

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """Creates necessary tables if they don't exist."""
        conn = self.connect()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS historical_data (
                        timestamp INTEGER,
                        symbol TEXT,
                        open REAL,
                        high REAL,
                        low REAL,
                        close REAL,
                        volume REAL,
                        PRIMARY KEY (timestamp, symbol)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trades (
                        trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp INTEGER,
                        symbol TEXT,
                        side TEXT,
                        order_type TEXT,
                        price REAL,
                        size REAL,
                        profit_loss REAL,
                        status TEXT
                    )
                """)
                conn.commit()
                print("Tables created successfully (if not already present).")
            except sqlite3.Error as e:
                print(f"Error creating tables: {e}")
            finally:
                self.close()

    def insert_historical_data(self, data):
        """Inserts historical kline data into the database."""
        conn = self.connect()
        if conn and data:
            cursor = conn.cursor()
            try:
                cursor.executemany("""
                    INSERT OR IGNORE INTO historical_data (timestamp, symbol, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, [(
                    int(d['timestamp']),  # Timestamp from ccxt data
                    data['symbol'],
                    float(d['open']), # Open
                    float(d['high']), # High
                    float(d['low']), # Low
                    float(d['close']), # Close
                    float(d['volume'])  # Volume
                ) for d in data['data']]) # 'data' key assumed from API client (modified to use ccxt data format)
                conn.commit()
                print(f"Inserted {len(data['data'])} historical data points for {data['symbol']}.")
            except sqlite3.Error as e:
                print(f"Error inserting historical data: {e}")  # <--- Line 162 is in this block in *my* code
            finally:
                self.close()

    def log_trade(self, trade_data):
        """Logs a trade into the database."""
        conn = self.connect()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO trades (timestamp, symbol, side TEXT, order_type TEXT, price REAL, size REAL, profit_loss REAL, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    int(trade_data['timestamp']),
                    trade_data['symbol'],
                    trade_data['side'],
                    trade_data['order_type'],
                    trade_data['price'],
                    trade_data['size'],
                    trade_data['profit_loss'],
                    trade_data['status']
                ))
                conn.commit()
                print(f"Logged trade for {trade_data['symbol']} - {trade_data['side']} {trade_data['size']} @ {trade_data['price']}")
            except sqlite3.Error as e:
                print(f"Error logging trade: {e}")
            finally:
                self.close()

    def fetch_recent_historical_data(self, symbol, limit=100):
        """Fetches recent historical data for a symbol from the database (example)."""
        conn = self.connect()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    SELECT timestamp, open, high, low, close, volume
                    FROM historical_data
                    WHERE symbol = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (symbol, limit))
                rows = cursor.fetchall()
                return rows
            except sqlite3.Error as e:
                print(f"Error fetching recent historical data: {e}")
                return None
            finally:
                self.close()
        return None


# --- TRADING STRATEGY --- (Modified - MACD Confirmation - CORRECTED COLUMN NAMES)
class TradingStrategy:
    def __init__(self):
        self.rsi_period = RSI_PERIOD
        self.rsi_oversold = RSI_OVERSOLD
        self.rsi_overbought = RSI_OVERBOUGHT
        self.db_manager = DatabaseManager() # Instantiate DatabaseManager to fetch historical data
        self.sma_period = SMA_PERIOD
        self.macd_fast_period = MACD_FAST_PERIOD # <-- Add MACD Periods
        self.macd_slow_period = MACD_SLOW_PERIOD # <-- Add MACD Periods
        self.macd_signal_period = MACD_SIGNAL_PERIOD # <-- Add MACD Periods

    def analyze_market(self, symbol):
        """Analyzes market data with RSI and MACD confirmation, returns trading signal. **SMA CONDITION TEMPORARILY REMOVED FOR TESTING**"""
        historical_data_rows = self.db_manager.fetch_recent_historical_data(symbol, limit=max(self.rsi_period, self.sma_period, self.macd_slow_period) + 20) # Fetch enough data for all indicators

        if not historical_data_rows or len(historical_data_rows) < max(self.rsi_period, self.sma_period, self.macd_slow_period): # Ensure enough data for all
            print(f"Insufficient historical data for RSI, SMA, and MACD calculation for {symbol}")
            return "neutral" # Not enough data

        # Convert historical data rows to a Pandas DataFrame
        df = pd.DataFrame(historical_data_rows, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['close'] = pd.to_numeric(df['close']) # Ensure 'close' is numeric

        # Calculate RSI using pandas-ta
        rsi_series = pta.rsi(df['close'], length=self.rsi_period) # Calculate RSI using pandas-ta
        current_rsi = rsi_series.iloc[-1] # Get the latest RSI value

        # Calculate SMA using pandas-ta
        sma_series = pta.sma(df['close'], length=self.sma_period) # Calculate SMA
        current_sma = sma_series.iloc[-1] # Get the latest SMA value
        current_price = df['close'].iloc[-1] # Get latest price

        # Calculate MACD using pandas-ta
        macd_series = pta.macd(df['close'], fast=self.macd_fast_period, slow=self.macd_slow_period, signal=self.macd_signal_period)

        # --- DEBUG: macd_series DataFrame ---  <--- DEBUG PRINT - KEEP FOR NOW TO VERIFY COLUMN NAMES
        print("\n--- DEBUG: macd_series DataFrame ---")
        print(macd_series)
        print("--- DEBUG: End macd_series DataFrame ---\n")
        # --- DEBUG: macd_series DataFrame ---

        # CORRECTED MACD COLUMN NAMES - assuming pandas-ta standard output
        macd_line_column_name = f'MACD_{self.macd_fast_period}_{self.macd_slow_period}_{self.macd_signal_period}' # Construct MACD Line column name
        macd_signal_column_name = f'MACDs_{self.macd_fast_period}_{self.macd_slow_period}_{self.macd_signal_period}' # Construct MACD Signal column name


        current_macd = macd_series[macd_line_column_name].iloc[-1] # Get latest MACD Line value - CORRECTED COLUMN NAME
        current_macd_signal = macd_series[macd_signal_column_name].iloc[-1] # Get latest MACD Signal Line value - CORRECTED COLUMN NAME


        signal = "neutral" # Default signal

        if current_rsi < self.rsi_oversold: # Oversold condition
            # if current_price > current_sma: # Price above SMA - Long confirmation  <-- COMMENTED OUT
            if current_macd > current_macd_signal: # MACD bullish crossover - further Long confirmation
                signal = "long"
            else:
                print(f"RSI Oversold & Price above SMA for {symbol}, but MACD not bullish. Neutral signal.") # Optional: Log MACD filter # <-- Original log, now inaccurate but can leave it
                signal = "neutral" # Remain neutral if MACD condition not met  # <-- Changed to neutral in original, keep for now, might remove completely later
            # else:  # <-- COMMENTED OUT
            #     print(f"RSI Oversold for {symbol}, but price below SMA. Neutral signal.") # Optional: Log SMA filter # <-- COMMENTED OUT
            #     signal = "neutral" # Remain neutral if SMA condition not met # <-- COMMENTED OUT

        elif current_rsi > self.rsi_overbought: # Overbought condition
            # if current_price < current_sma: # Price below SMA - Short confirmation  <-- COMMENTED OUT
            if current_macd < current_macd_signal: # MACD bearish crossover - further Short confirmation
                signal = "short"
            else:
                print(f"RSI Overbought & Price below SMA for {symbol}, but MACD not bearish. Neutral signal.") # Optional: Log MACD filter # <-- Original log, now inaccurate but can leave it
                signal = "neutral" # Remain neutral if MACD condition not met # <-- Changed to neutral in original, keep for now, might remove completely later
            # else: # <-- COMMENTED OUT
            #     print(f"RSI Overbought for {symbol}, but price above SMA. Neutral signal.") # Optional: Log SMA filter # <-- COMMENTED OUT
            #     signal = "neutral" # Remain neutral if SMA condition not met # <-- COMMENTED OUT
        else:
            signal = "neutral" # RSI in neutral zone

        return signal


# --- TRADING BOT --- (No UI - Strategy Enhanced with MACD - CORRECTED COLUMN NAMES)
class TradingBot:
    def __init__(self):
        self.api_client = CcxtKucoinAPIClient() #  <---  USE CcxtKucoinAPIClient now
        active_symbols = self.api_client.get_active_trade_symbols() # Fetch symbols directly here
        print(f"Debug: TradingBot.__init__() - Fetched {len(active_symbols)} active symbols.") # Debug print: count in TradingBot init
        self.api_client.print_active_symbols() # <-- ADDED LINE to print active symbols
        self.db_manager = DatabaseManager()
        self.strategy = TradingStrategy()
        self.trade_symbols = TRADE_SYMBOLS
        self.klines_interval = '1m' # ccxt timeframes are different, '1m' for 1 minute
        self.db_manager.create_tables() # Ensure tables exist
        self.initial_balance = None # To track drawdown


    def fetch_historical_data_and_store(self, symbol, periods_ago='1 week'):
        """Fetches historical data for a symbol and stores it in the database using ccxt."""
        end_time_ms = self.exchange_time_to_milliseconds(self.api_client.exchange.milliseconds()) # Current time in milliseconds for ccxt
        start_time_ms = end_time_ms - self.time_to_milliseconds(periods_ago) # Calculate start time
        timeframe_ccxt = '1m' # Consistent 1-minute timeframe for ccxt

        historical_data_ccxt = self.api_client.get_historical_data(symbol, timeframe_ccxt, start_time_ms) # Fetch with ccxt

        if historical_data_ccxt:
            data_to_insert = {'symbol': symbol, 'data': historical_data_ccxt} # Prepare for DB insert (using ccxt data format)
            self.db_manager.insert_historical_data(data_to_insert) # Store in DB
            return True # Data fetched and stored
        return False # Failed

    def exchange_time_to_milliseconds(self, exchange_timestamp):
        """Converts exchange timestamp to milliseconds (if needed - ccxt timestamps are usually in ms)."""
        return int(exchange_timestamp) # Assuming ccxt timestamps are already milliseconds

    def time_to_milliseconds(self, time_period_str):
        """Converts a time period string (e.g., '1 week', '2 days') to milliseconds."""
        time_units = time_period_str.split()
        value = int(time_units[0])
        unit = time_units[1].lower()

        if unit == 'week' or unit == 'weeks':
            return value * 7 * 24 * 60 * 60 * 1000
        elif unit == 'day' or unit == 'days':
            return value * 24 * 60 * 60 * 1000
        elif unit == 'hour' or unit == 'hours':
            return value * 60 * 60 * 1000
        elif unit == 'minute' or unit == 'minutes':
            return value * 60 * 1000
        # Add more time units as needed (seconds, etc.)
        else:
            raise ValueError(f"Unsupported time unit: {unit}")


    def calculate_order_size(self, symbol, entry_price, balance):
        """Calculates order size based on risk percentage and account balance."""
        risk_percent_per_trade = RISK_PER_TRADE_PERCENT # Use global config
        if not entry_price or not balance or balance <= 0:
            return 0 # Cannot calculate order size

        risk_amount_usd = balance * risk_percent_per_trade # USD amount to risk
        order_size_usd = risk_amount_usd
        order_qty = order_size_usd / entry_price # Quantity in base currency (e.g., BTC)

        # Minimum order size check (ensure it meets KuCoin's minimum notional value)
        min_order_qty_based_on_notional = MIN_ORDER_NOTIONAL / entry_price # Min quantity based on min notional
        order_qty = max(order_qty, min_order_qty_based_on_notional) # Ensure minimum order size

        return order_qty

    def check_sufficient_balance(self, symbol, order_size_usd, current_balance):
        """Checks if balance is sufficient for the order."""
        if not current_balance:
            return False # Cannot check if no balance info available

        required_balance = order_size_usd #  Simplified - in reality margin calculation is more complex
        if current_balance >= required_balance:
            return True
        else:
            print(f"Insufficient balance ({current_balance} USDT) for order value of {order_size_usd} USDT.")
            return False

    def check_drawdown(self, current_balance):
        """Checks if max drawdown limit is reached."""
        if self.initial_balance is not None and self.initial_balance > 0 and current_balance is not None: # Ensure initial_balance is valid and > 0
            drawdown = 1 - (current_balance / self.initial_balance) # Drawdown as a fraction
            if drawdown >= MAX_DRAWDOWN_PERCENT: # Use global config
                print(f"Maximum Drawdown ({MAX_DRAWDOWN_PERCENT*100}%) reached! Stopping bot.")
                return True # Drawdown limit reached
        return False

    def run_bot(self):
        """Main bot execution loop."""
        print("Starting KuCoin Futures Trading Bot (Single File)...")
        initial_balance = self.api_client.get_account_balance() # Use ccxt client to get balance

        if initial_balance is None:
            print("Error fetching initial balance from KuCoin API (ccxt). Bot exiting.") # More specific error message
            return

        if initial_balance <= 0: # Check if initial_balance is zero or negative
            print(f"Error: Initial balance fetched was {initial_balance} USDT (ccxt).  Bot requires a positive balance to start. Please check your KuCoin Futures account balance and API key/secret/passphrase.")
            return # Exit if initial balance is not positive


        self.initial_balance = initial_balance # Set initial balance for drawdown tracking
        print(f"Initial balance: {self.initial_balance} USDT (ccxt). Starting trading loop.") # Confirm initial balance

        while True:
            current_balance = self.api_client.get_account_balance() # Use ccxt client to get balance
            if current_balance is None:
                print("Error fetching current balance (ccxt). Retrying in next cycle.")
                time.sleep(60) # Wait and retry
                continue

            if self.check_drawdown(current_balance): # Check for max drawdown
                print("Bot stopped due to maximum drawdown.")
                break # Stop the bot

            for symbol in self.trade_symbols:
                print(f"--- Analyzing {symbol} ---")

                # 1. Fetch Recent Historical Data & Update DB
                if not self.fetch_historical_data_and_store(symbol, periods_ago='2 hours'): # Fetch last 2 hours of data before analysis each cycle
                    print(f"Failed to fetch recent historical data for {symbol}. Skipping analysis for this cycle.")
                    continue # Skip to next symbol

                # 2. Market Analysis (Strategy)
                trading_signal = self.strategy.analyze_market(symbol)
                print(f"Trading Signal for {symbol}: {trading_signal}")

                position = self.api_client.get_position(symbol) # Check for existing position

                if trading_signal == "long" and (not position or position['side'] != 'long'): # Signal to go long, and no existing long position
                    if position and position['side'] == 'short': # Close existing short position first
                        print(f"Closing existing short position for {symbol} before opening long.")
                        close_order = self.api_client.close_position(symbol, 'short')
                        if not close_order:
                            print(f"Failed to close short position for {symbol}. Skipping long entry this cycle.")
                            continue # Skip to next symbol if close failed
                        time.sleep(2) # Wait briefly after closing position

                    ticker = self.api_client.get_ticker(symbol)
                    if not ticker:
                        print(f"Could not get ticker for {symbol}. Skipping long entry.")
                        continue
                    entry_price = float(ticker['bestAsk']) # Use best ask for market buy
                    order_size = self.calculate_order_size(symbol, entry_price, current_balance) # Calculate size based on risk

                    if order_size > 0:
                        if self.check_sufficient_balance(symbol, order_size * entry_price, current_balance):
                            print(f"Placing Long order for {symbol}, Size: {order_size}")
                            order_result = self.api_client.place_order(symbol, 'buy', 'market', order_size)
                            if order_result:
                                trade_data = { # Log trade details
                                    'timestamp': int(time.time() * 1000),
                                    'symbol': symbol,
                                    'side': 'buy',
                                    'order_type': 'market',
                                    'price': entry_price,
                                    'size': order_size,
                                    'profit_loss': 0, # Profit/loss tracked later on position updates
                                    'status': 'open' # Initial status
                                }
                                self.db_manager.log_trade(trade_data)
                            else:
                                print(f"Failed to place Long order for {symbol}")
                        else:
                            print(f"Insufficient balance for Long order on {symbol}")
                    else:
                        print(f"Calculated order size is too small or zero for Long on {symbol}. Not placing order.")


                elif trading_signal == "short" and (not position or position['side'] != 'short'): # Signal to go short, no existing short

                    if position and position['side'] == 'long': # Close existing long position first
                        print(f"Closing existing long position for {symbol} before opening short.")
                        close_order = self.api_client.close_position(symbol, 'long')
                        if not close_order:
                            print(f"Failed to close long position for {symbol}. Skipping short entry this cycle.")
                            continue
                        time.sleep(2) # Wait briefly

                    ticker = self.api_client.get_ticker(symbol)
                    if not ticker:
                        print(f"Could not get ticker for {symbol}. Skipping short entry.")
                        continue
                    entry_price = float(ticker['bestBid']) # Use best bid for market sell (short)
                    order_size = self.calculate_order_size(symbol, entry_price, current_balance)

                    if order_size > 0:
                         if self.check_sufficient_balance(symbol, order_size * entry_price, current_balance):
                            print(f"Placing Short order for {symbol}, Size: {order_size}")
                            order_result = self.api_client.place_order(symbol, 'sell', 'market', order_size)
                            if order_result:
                                trade_data = { # Log trade details
                                    'timestamp': int(time.time() * 1000),
                                    'symbol': symbol,
                                    'side': 'sell',
                                    'order_type': 'market',
                                    'price': entry_price,
                                    'size': order_size,
                                    'profit_loss': 0,
                                    'status': 'open'
                                }
                                self.db_manager.log_trade(trade_data)
                            else:
                                print(f"Failed to place Short order for {symbol}")
                         else:
                            print(f"Insufficient balance for Short order on {symbol}")
                    else:
                        print(f"Calculated order size is too small or zero for Short on {symbol}. Not placing order.")


                elif trading_signal == "neutral" or (position and position['side'] and trading_signal != position['side']): # Or signal changes direction
                    if position and position['side']: # Close existing position if neutral signal or signal direction changes
                        print(f"Neutral signal or signal change for {symbol}. Closing existing {position['side']} position.")
                        close_order = self.api_client.close_position(symbol, position['side'])
                        if close_order:
                             print(f"Closed {position['side']} position for {symbol}.")
                             # Update trade log with closing status and profit/loss (more advanced)
                        else:
                            print(f"Failed to close position for {symbol}.")

                else:
                    print(f"Holding existing position for {symbol} - no action.")


            print("Cycle complete. Waiting before next analysis...")
            time.sleep(60) # Check market every 60 seconds (adjust cycle time as needed)

if __name__ == "__main__":
    bot = TradingBot()
    bot.run_bot()
