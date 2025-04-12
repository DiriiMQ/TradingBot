import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands
import logging
from typing import Dict, Optional, List
from datetime import datetime

class TradingStrategy:
    def __init__(self):
        """Initialize the trading strategy"""
        self.positions: Dict[str, Dict] = {}
        self.performance_metrics: Dict[str, Dict] = {}
        
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

    def generate_recommendations(self, stock_info, symbols: List[str]) -> List[Dict]:
        """Generate trading recommendations with risk management"""
        recommendations = []
        
        for symbol in symbols:
            logging.info(f"Analyzing {symbol}...")
            df = stock_info.get_historical_data(symbol)
            trend = self.analyze_trend(df)
            
            if trend:
                # Calculate position size
                position_size = stock_info.calculate_position_size(
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