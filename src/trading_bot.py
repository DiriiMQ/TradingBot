import logging
from datetime import datetime
from stock_info import StockInfo
from strategy import TradingStrategy

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
        self.stock_info = StockInfo()
        self.strategy = TradingStrategy()
        self.risk_per_trade = risk_per_trade
        self.max_position_size = max_position_size

    def run(self):
        """Main execution method"""
        logging.info("Starting trading bot analysis...")
        recommendations = self.strategy.generate_recommendations(
            self.stock_info,
            self.stock_info.symbols
        )
        
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