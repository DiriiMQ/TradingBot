import pandas as pd
import numpy as np
from vnstock import Vnstock
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands
import logging
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional, Tuple

# Load environment variables
load_dotenv()

EXCHANGE_VCI = 'VCI'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)

class TradingBot:
    def __init__(self, risk_per_trade: float = 0.02, max_position_size: float = 0.1):
        """
        Initialize the trading bot with risk management parameters
        
        Args:
            risk_per_trade (float): Maximum risk per trade as a percentage of capital (default: 2%)
            max_position_size (float): Maximum position size as a percentage of capital (default: 10%)
        """
        self.vnstock = Vnstock()
        self.symbols = self._load_symbols()
        self.risk_per_trade = risk_per_trade
        self.max_position_size = max_position_size
        self.positions: Dict[str, Dict] = {}
        self.performance_metrics: Dict[str, Dict] = {}
        
    def _load_symbols(self) -> List[str]:
        """Load list of symbols to analyze"""
        return ['VCI', 'VNM', 'FPT', 'VHM', 'VIB']
    
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

    def calculate_position_size(self, symbol: str, price: float, stop_loss: float) -> int:
        """
        Calculate position size based on risk management rules
        
        Args:
            symbol (str): Trading symbol
            price (float): Current price
            stop_loss (float): Stop loss price
            
        Returns:
            int: Number of shares to trade
        """
        try:
            # Get account balance (simulated for now)
            account_balance = 100000000  # 100M VND
            
            # Calculate risk amount
            risk_amount = account_balance * self.risk_per_trade
            
            # Calculate position size based on risk
            price_risk = abs(price - stop_loss)
            position_size = int(risk_amount / price_risk)
            
            # Apply maximum position size limit
            max_shares = int(account_balance * self.max_position_size / price)
            position_size = min(position_size, max_shares)
            
            return position_size
        except Exception as e:
            logging.error(f"Error calculating position size for {symbol}: {str(e)}")
            return 0

    def analyze_trend(self, df: pd.DataFrame) -> Optional[Dict]:
        """Analyze trend using multiple technical indicators"""
        if df is None or df.empty:
            return None
            
        # Calculate technical indicators
        sma_20 = SMAIndicator(close=df['close'], window=20)
        sma_50 = SMAIndicator(close=df['close'], window=50)
        ema_20 = EMAIndicator(close=df['close'], window=20)
        rsi = RSIIndicator(close=df['close'])
        stoch = StochasticOscillator(high=df['high'], low=df['low'], close=df['close'])
        bb = BollingerBands(close=df['close'])
        macd = MACD(close=df['close'])
        
        # Add indicators to DataFrame
        df['sma_20'] = sma_20.sma_indicator()
        df['sma_50'] = sma_50.sma_indicator()
        df['ema_20'] = ema_20.ema_indicator()
        df['rsi'] = rsi.rsi()
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_lower'] = bb.bollinger_lband()
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        
        # Get latest values
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Calculate stop loss and take profit levels
        atr = self._calculate_atr(df)
        stop_loss = latest['close'] - (2 * atr)  # 2 ATR for stop loss
        take_profit = latest['close'] + (4 * atr)  # 4 ATR for take profit
        
        # Trend analysis with multiple confirmations
        trend = {
            'price': latest['close'],
            'sma_20': latest['sma_20'],
            'sma_50': latest['sma_50'],
            'ema_20': latest['ema_20'],
            'rsi': latest['rsi'],
            'stoch_k': latest['stoch_k'],
            'stoch_d': latest['stoch_d'],
            'bb_upper': latest['bb_upper'],
            'bb_lower': latest['bb_lower'],
            'macd': latest['macd'],
            'macd_signal': latest['macd_signal'],
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'trend': self._determine_trend(latest, prev),
            'momentum': self._determine_momentum(latest),
            'volatility': self._determine_volatility(latest, atr)
        }
        
        return trend

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr.iloc[-1]

    def _determine_trend(self, latest: pd.Series, prev: pd.Series) -> str:
        """Determine trend using multiple indicators"""
        trend_signals = []
        
        # SMA crossover
        if latest['sma_20'] > latest['sma_50']:
            trend_signals.append(1)
        else:
            trend_signals.append(-1)
            
        # EMA trend
        if latest['ema_20'] > latest['sma_50']:
            trend_signals.append(1)
        else:
            trend_signals.append(-1)
            
        # MACD
        if latest['macd'] > latest['macd_signal']:
            trend_signals.append(1)
        else:
            trend_signals.append(-1)
            
        # Average the signals
        avg_signal = sum(trend_signals) / len(trend_signals)
        
        if avg_signal > 0.5:
            return 'Strong Bullish'
        elif avg_signal > 0:
            return 'Bullish'
        elif avg_signal < -0.5:
            return 'Strong Bearish'
        else:
            return 'Bearish'

    def _determine_momentum(self, latest: pd.Series) -> str:
        """Determine momentum using RSI and Stochastic"""
        if latest['rsi'] > 70 and latest['stoch_k'] > 80:
            return 'Strong Overbought'
        elif latest['rsi'] > 70:
            return 'Overbought'
        elif latest['rsi'] < 30 and latest['stoch_k'] < 20:
            return 'Strong Oversold'
        elif latest['rsi'] < 30:
            return 'Oversold'
        else:
            return 'Neutral'

    def _determine_volatility(self, latest: pd.Series, atr: float) -> str:
        """Determine volatility state"""
        bb_width = (latest['bb_upper'] - latest['bb_lower']) / latest['close']
        
        if bb_width > 0.05:  # 5% bandwidth
            return 'High'
        elif bb_width > 0.03:  # 3% bandwidth
            return 'Medium'
        else:
            return 'Low'

    def generate_recommendations(self) -> List[Dict]:
        """Generate trading recommendations with risk management"""
        recommendations = []
        
        for symbol in self.symbols:
            logging.info(f"Analyzing {symbol}...")
            df = self.get_historical_data(symbol)
            trend = self.analyze_trend(df)
            
            if trend:
                # Calculate position size
                position_size = self.calculate_position_size(
                    symbol,
                    trend['price'],
                    trend['stop_loss']
                )
                
                recommendation = {
                    'symbol': symbol,
                    'price': trend['price'],
                    'trend': trend['trend'],
                    'momentum': trend['momentum'],
                    'volatility': trend['volatility'],
                    'rsi': trend['rsi'],
                    'stop_loss': trend['stop_loss'],
                    'take_profit': trend['take_profit'],
                    'position_size': position_size,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Generate trading signal with multiple confirmations
                if (trend['trend'] in ['Strong Bullish', 'Bullish'] and 
                    trend['momentum'] in ['Strong Oversold', 'Oversold'] and
                    trend['volatility'] != 'High'):
                    recommendation['signal'] = 'BUY'
                elif (trend['trend'] in ['Strong Bearish', 'Bearish'] and 
                      trend['momentum'] in ['Strong Overbought', 'Overbought'] and
                      trend['volatility'] != 'High'):
                    recommendation['signal'] = 'SELL'
                else:
                    recommendation['signal'] = 'HOLD'
                
                recommendations.append(recommendation)
                logging.info(f"Recommendation for {symbol}: {recommendation['signal']}")
        
        return recommendations

    def update_performance_metrics(self, symbol: str, trade_data: Dict):
        """Update performance metrics for a symbol"""
        if symbol not in self.performance_metrics:
            self.performance_metrics[symbol] = {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'total_profit': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0
            }
        
        metrics = self.performance_metrics[symbol]
        metrics['total_trades'] += 1
        
        if trade_data['profit'] > 0:
            metrics['winning_trades'] += 1
        else:
            metrics['losing_trades'] += 1
            
        metrics['total_profit'] += trade_data['profit']
        
        # Update max drawdown if necessary
        current_drawdown = trade_data.get('drawdown', 0)
        metrics['max_drawdown'] = max(metrics['max_drawdown'], current_drawdown)
        
        # Calculate win rate
        metrics['win_rate'] = metrics['winning_trades'] / metrics['total_trades']
        
        # Calculate average profit per trade
        metrics['avg_profit'] = metrics['total_profit'] / metrics['total_trades']

    def run(self):
        """Main execution method"""
        logging.info("Starting trading bot analysis...")
        recommendations = self.generate_recommendations()
        
        # Log recommendations with detailed analysis
        for rec in recommendations:
            logging.info(f"""
            Symbol: {rec['symbol']}
            Signal: {rec['signal']}
            Price: {rec['price']}
            Trend: {rec['trend']}
            Momentum: {rec['momentum']}
            Volatility: {rec['volatility']}
            RSI: {rec['rsi']:.2f}
            Stop Loss: {rec['stop_loss']:.2f}
            Take Profit: {rec['take_profit']:.2f}
            Position Size: {rec['position_size']}
            Time: {rec['timestamp']}
            """)
        
        logging.info("Trading bot analysis completed.")

if __name__ == "__main__":
    bot = TradingBot()
    bot.run() 