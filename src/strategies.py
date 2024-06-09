from decision import DecisionStatus, DecisionSystem
from utils import TradingView_TA, TVData, Interval, TVInterval, bcolors
from symbol_st import Symbol
import time

class NPN_Maker(DecisionSystem):
    def __init__(self):
        self.potential_symbols = []
        self.all_symbols = []
        self.symbols_analysis = {}
        self.interval = Interval.INTERVAL_5_MINUTES
        self.GAP_REQUEST = 0.01

    def should_buy(self, symbol: Symbol) -> DecisionStatus:
        for i in self.potential_symbols[:20]:
            if i[1] == symbol.symbol:
                hist = TVData.get_tvdata_hist(symbol.symbol, symbol.exchange, TVInterval.in_3_minute, 3)
                # time.sleep(self.GAP_REQUEST)    
                # check if the average of 3 last bars is non decreasing
                # make sure that the last bars are green (close > open) 
                if float(hist[3][5]) > float(hist[2][5]) and float(hist[2][5]) > float(hist[1][5]) \
                    and float(hist[3][5]) > float(hist[3][2]) \
                    and float(hist[2][5]) > float(hist[2][2]) \
                    and float(hist[1][5]) > float(hist[1][2]):
                    return DecisionStatus.BUY
        return DecisionStatus.NEUTRAL

    def should_sell(self, symbol: Symbol) -> DecisionStatus:
        try:
            analysis = TradingView_TA.get_analysis(symbol.symbol, symbol.screener, symbol.exchange, self.interval)
        except Exception as e:
            print('Error:', e)
            return DecisionStatus.NEUTRAL

        if analysis is None:
            print('Analysis for symbol', symbol.symbol, 'is None')
            return DecisionStatus.NEUTRAL

        if analysis.summary['RECOMMENDATION'] == 'SELL':
            return DecisionStatus.SELL
        
        current_price = analysis.indicators['close']

        # difference than 0.05% -> sell // cut loss
        if current_price < symbol.boughtPrice * (1 - 0.05):
            return DecisionStatus.SELL
        
        # current price is 0.01% higher than bought price -> sell
        if current_price > symbol.boughtPrice * (1 + 0.01):
            print(bcolors.OKCYAN + 'Take profit' + bcolors.ENDC, symbol.symbol, current_price, symbol.boughtPrice)
            return DecisionStatus.SELL
        
        return DecisionStatus.NEUTRAL

    def get_advice(self, symbol: Symbol) -> DecisionStatus:
        sttBuy = self.should_buy(symbol)

        if symbol.availableAmount == 0:
            return sttBuy
        
        sttSell = self.should_sell(symbol)
        
        if sttSell == DecisionStatus.SELL:
            return sttSell
        
        return sttBuy
    
    def initialize(self, all_symbols: list):
        self.all_symbols = all_symbols
        self.update()
        return self

    def update(self) -> None:
        queried_symbols = []

        for symbol in self.all_symbols:
            queried_symbols.append(self.all_symbols[0].exchange + ':' + symbol.symbol)

        self.symbols_analysis = TradingView_TA.get_multiple_analysis(self.all_symbols[0].screener, self.interval, queried_symbols)
        evaluated_symbols = []

        for i in queried_symbols:
            # print(symbols_analysis[i], i)
            if self.symbols_analysis[i] is not None:
                evaluated_symbols.append([self.symbols_analysis[i].summary['BUY'], i.removeprefix(self.all_symbols[0].exchange + ':')])

        evaluated_symbols.sort(reverse=True)
        self.potential_symbols = evaluated_symbols

        print(self.potential_symbols[:20])

    def get_potential_symbols(self):
        self.update()
        return self.potential_symbols[:20]
        