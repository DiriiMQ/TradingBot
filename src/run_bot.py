from trading_bot import TradingBot
import schedule
import time

def job():
    bot = TradingBot()
    bot.run()

def main():
    # Run immediately when starting
    job()
    
    # Schedule to run every day at 15:30 (market close)
    schedule.every().day.at("15:30").do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main() 