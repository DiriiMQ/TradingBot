from abc import ABC, abstractmethod
from symbol_st import Symbol
from enum import Enum

class DecisionStatus(Enum):
    SELL = 0
    BUY = 1
    NEUTRAL = 2

class DecisionSystem(ABC):
    potential_symbols = []
    all_symbols = []

    @abstractmethod
    def should_buy(self, symbol: Symbol) -> DecisionStatus:
        pass

    @abstractmethod
    def should_sell(self, symbol: Symbol) -> DecisionStatus:
        pass

    @abstractmethod
    def get_advice(self, symbol: Symbol) -> DecisionStatus:
        pass

    @abstractmethod
    def initialize(self, all_symbols: list) -> None:
        pass

    @abstractmethod
    def update(self) -> None:
        pass

    @abstractmethod
    def get_potential_symbols(self) -> list:
        pass