from decision import DecisionStatus, DecisionSystem
from symbol_st import Symbol
from abc import ABC, abstractmethod

class TradingSystem(ABC):
    available_symbols = []
    all_symbols = []

    @abstractmethod
    def initialize(self): # get all available symbols and its available amount
        pass

    def get_decision(self, symbol: Symbol, maker: DecisionSystem) -> DecisionStatus:
        return maker.get_advice(symbol)

    @abstractmethod
    def buy(self, symbol: Symbol, quantity: float) -> None:
        pass

    @abstractmethod
    def sell(self, symbol: Symbol, quantity: float) -> None:
        pass

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def loop(self) -> None: # maybbe need this function
        pass
