from tradingview_ta import TA_Handler, Interval, Exchange, get_multiple_analysis
from tvDatafeed import TvDatafeed, Interval as TVInterval
import time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class TradingView_TA:
    @staticmethod
    def get_analysis(symbol: str, screener: str, exchange: str, interval: Interval) -> TA_Handler:
        handler = TA_Handler(
            symbol=symbol,
            screener=screener,
            exchange=exchange,
            interval=interval,
        )
        return handler.get_analysis()

    @staticmethod
    def get_summary(symbol: str, screener: str, exchange: str, interval: Interval) -> dict:
        handler = TA_Handler(
            symbol=symbol,
            screener=screener,
            exchange=exchange,
            interval=interval,
        )
        return handler.get_analysis().summary

    @staticmethod
    def get_indicators(symbol: str, screener: str, exchange: str, interval: Interval) -> dict:
        handler = TA_Handler(
            symbol=symbol,
            screener=screener,
            exchange=exchange,
            interval=interval,
        )
        return handler.get_analysis().indicators
    
    # Format: {"EXCHANGE:SYMBOL": Analysis}
    @staticmethod
    def get_multiple_analysis(screener: str, interval: Interval, symbols: list) -> dict:
        return get_multiple_analysis(screener=screener, interval=interval, symbols=symbols)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class TVData:
    tv = TvDatafeed()

    @staticmethod
    def get_tvdata_hist(symbol: str, exchange: str, interval: TVInterval, n_bars: int) -> list:
        hist = TVData.tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=n_bars)
        if hist is None:
            time.sleep(0.05)
            return TVData.get_tvdata_hist(symbol, exchange, interval, n_bars)
        dt = hist.to_csv().splitlines()
        for i in range(len(dt)):
            dt[i] = dt[i].split(',')
        return dt
    
class BinanceInstance:
    pass
