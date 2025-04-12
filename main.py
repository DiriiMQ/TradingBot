from src.trading_bot import TradingBot
import schedule
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)

def run_trading_bot():
    """Execute the trading bot analysis"""
    bot = TradingBot()
    bot.run()

def main():
    # Run immediately when starting
    logging.info("Starting trading bot...")
    run_trading_bot()
    
    # Schedule to run every day at 15:30 (market close)
    schedule.every().day.at("15:30").do(run_trading_bot)
    
    logging.info("Trading bot scheduled to run daily at 15:30")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
