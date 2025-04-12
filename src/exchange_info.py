import pandas as pd
from vnstock import Vnstock
import logging
from typing import Optional, Dict, List, Union

class ExchangeInfo:
    # Vietnamese exchange symbols
    VN_EXCHANGES = [
        # Main exchanges
        'HOSE',  # Ho Chi Minh Stock Exchange
        'HNX',   # Hanoi Stock Exchange
        'UPCOM', # Unlisted Public Company Market
        
        # VNIndex segments
        'VN30',      # VN30 Index
        'VNMidCap',  # VNMidCap Index
        'VNSmallCap',# VNSmallCap Index
        'VNAllShare',# VNAllShare Index
        'VN100',     # VN100 Index
        
        # HNX segments
        'HNX30',    # HNX30 Index
        'HNXCon',   # HNX Construction Index
        'HNXFin',   # HNX Finance Index
        'HNXLCap',  # HNX Large Cap Index
        'HNXMSCap', # HNX Mid & Small Cap Index
        'HNXMan',   # HNX Manufacturing Index
        
        # Special segments
        'ETF',      # Exchange Traded Funds
        'FU_INDEX', # Futures Index
        'CW'        # Covered Warrants
    ]

    def __init__(self):
        """Initialize the exchange information handler"""
        self.vnstock = Vnstock()
        self.stock_info = self.vnstock.stock()
        self._exchange_data = None
        self._symbol_info_map = {}

    def get_all_available_groups(self) -> List[str]:
        """Get all available groups"""
        return self.VN_EXCHANGES

    def _load_all_symbols_by_group(self, group: str) -> pd.Series:
        """
        Load all symbols from Vnstock by group
        
        Returns a pandas Series with the list of symbols in the group
        For example:
        0     ACB
        1     BCM
        2     BID
        """
        if group not in self.VN_EXCHANGES:
            raise ValueError(f"Invalid group: {group}")
        return self.stock_info.listing.symbols_by_group(group)

    def _load_all_symbols_by_exchanges(self) -> pd.DataFrame:
        """
        Load all symbols from Vnstock
        Returns a pandas DataFrame with the following columns:
        - symbol: symbol code
        - exchange: exchange code
        - type: type of security (e.g., 'stock', 'etf', 'index')
        - organ_short_name: short name of the organization
        - organ_name: full name of the organization
        """
        if self._exchange_data is None:
            self._exchange_data = self.stock_info.listing.symbols_by_exchange()
            # Create a mapping of symbol to its info
            self._symbol_info_map = {
                row['symbol']: {
                    'exchange': row['exchange'],
                    'type': row['type'],
                    'organ_short_name': row['organ_short_name'],
                    'organ_name': row['organ_name']
                }
                for _, row in self._exchange_data.iterrows()
            }
        return self._exchange_data

    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """Get detailed information for a specific symbol"""
        if not self._symbol_info_map:
            self._load_all_symbols_by_exchanges()
        return self._symbol_info_map.get(symbol)

    def get_formatted_symbols_by_group(self, group: str) -> List[Dict[str, str]]:
        """
        Get formatted symbol data for a specific group
        
        Args:
            group (str): The exchange group (e.g., 'VN30', 'HOSE')
            
        Returns:
            List[Dict[str, str]]: List of dictionaries containing symbol information
            Each dictionary contains:
            - symbol: The stock symbol
            - type: The security type
            - organ_short_name: The organization's short name
        """
        if group not in self.VN_EXCHANGES:
            raise ValueError(f"Invalid group: {group}")
            
        # Load all symbols if not already loaded
        if self._exchange_data is None:
            self._load_all_symbols_by_exchanges()
            
        # Get symbols for the group
        symbols = self._load_all_symbols_by_group(group)
        
        # Format the data
        formatted_data = []
        for symbol in symbols:
            info = self._symbol_info_map.get(symbol, {})
            formatted_data.append({
                'symbol': symbol,
                'type': info.get('type', 'Unknown'),
                'organ_short_name': info.get('organ_short_name', 'Unknown')
            })
            
        return formatted_data 