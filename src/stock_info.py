import pandas as pd
from vnstock import Vnstock
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dotenv import load_dotenv
import json
import os
from pathlib import Path

# Load environment variables
load_dotenv()

EXCHANGE_VCI = 'VCI'
FAVORITE_SYMBOLS_FILE = 'data/favorite_symbols.json'
DEFAULT_FAVORITE_SYMBOLS = ['VCI', 'VNM', 'FPT', 'VHM', 'VIB']

class StockInfo:
    def __init__(self):
        """Initialize the stock information handler"""
        self.vnstock = Vnstock()
        self.symbols = self._load_symbols()
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        data_dir = Path('data')
        data_dir.mkdir(exist_ok=True)
        if not os.path.exists(FAVORITE_SYMBOLS_FILE):
            self._save_favorite_symbols(DEFAULT_FAVORITE_SYMBOLS)

    def _load_favorite_symbols(self) -> List[str]:
        """Load favorite symbols from file"""
        try:
            with open(FAVORITE_SYMBOLS_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _save_favorite_symbols(self, symbols: List[str]):
        """Save favorite symbols to file"""
        try:
            with open(FAVORITE_SYMBOLS_FILE, 'w') as f:
                json.dump(symbols, f, indent=4)
        except Exception as e:
            logging.error(f"Error saving favorite symbols: {str(e)}")

    def add_favorite_symbol(self, symbol: str) -> bool:
        """Add a symbol to favorites"""
        try:
            symbols = self._load_favorite_symbols()
            if symbol not in symbols:
                symbols.append(symbol)
                self._save_favorite_symbols(symbols)
                self.symbols = symbols  # Update the current symbols list
                return True
            return False
        except Exception as e:
            logging.error(f"Error adding favorite symbol: {str(e)}")
            return False

    def remove_favorite_symbol(self, symbol: str) -> bool:
        """Remove a symbol from favorites"""
        try:
            symbols = self._load_favorite_symbols()
            if symbol in symbols:
                symbols.remove(symbol)
                self._save_favorite_symbols(symbols)
                self.symbols = symbols  # Update the current symbols list
                return True
            return False
        except Exception as e:
            logging.error(f"Error removing favorite symbol: {str(e)}")
            return False

    def get_favorite_symbols(self) -> List[str]:
        """Get current list of favorite symbols"""
        return self._load_favorite_symbols()

    def _load_all_symbols_by_exchanges(self) -> List[str]:
        """Load all symbols from Vnstock"""
        return self.vnstock.stock().listing.symbols_by_exchange()
        
    def _load_symbols(self) -> List[str]:
        """Load list of symbols to analyze from favorites"""
        return self._load_favorite_symbols()
    
    def get_historical_data(self, symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Fetch historical data for a symbol"""
        try:
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
                
            stock = self.vnstock.stock(symbol=symbol, source=EXCHANGE_VCI)
            df = stock.quote.history(start=start_date, end=end_date)
            return df
        except Exception as e:
            logging.error(f"Error fetching data for {symbol}: {str(e)}")
            return None

    def calculate_position_size(self, symbol: str, price: float, stop_loss: float, risk_per_trade: float = 0.02, max_position_size: float = 0.1) -> int:
        """
        Calculate position size based on risk management rules
        
        Args:
            symbol (str): Trading symbol
            price (float): Current price
            stop_loss (float): Stop loss price
            risk_per_trade (float): Maximum risk per trade as a percentage of capital
            max_position_size (float): Maximum position size as a percentage of capital
            
        Returns:
            int: Number of shares to trade
        """
        try:
            # Get account balance (simulated for now)
            account_balance = 100000000  # 100M VND
            
            # Calculate risk amount
            risk_amount = account_balance * risk_per_trade
            
            # Calculate position size based on risk
            price_risk = abs(price - stop_loss)
            position_size = int(risk_amount / price_risk)
            
            # Apply maximum position size limit
            max_shares = int(account_balance * max_position_size / price)
            position_size = min(position_size, max_shares)
            
            return position_size
        except Exception as e:
            logging.error(f"Error calculating position size for {symbol}: {str(e)}")
            return 0 

if __name__ == "__main__":
    stock_info = StockInfo()
    print(stock_info._load_all_symbols_by_exchanges())