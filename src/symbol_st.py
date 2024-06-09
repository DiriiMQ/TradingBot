class Symbol:
    SELL_ALL = -1

    def __init__(self, symbol: str, screener: str, exchange: str) -> None:
        self.symbol = symbol
        self.screener = screener
        self.exchange = exchange
        self.availableAmount = 0.0
        self.boughtPrice = 0.0

    def __str__(self) -> str:
        return f'{self.symbol} - {self.screener} - {self.exchange} - {self.availableAmount}'
    
    def sell(self, quantity: float) -> int:
        if quantity > self.availableAmount:
            return -1
        
        if quantity == Symbol.SELL_ALL:
            self.availableAmount = 0
            self.boughtPrice = 0
            return 0
        
        self.availableAmount -= quantity
        return 0
    
    def buy(self, quantity: float, price: float) -> int:
        self.availableAmount += quantity
        self.boughtPrice = price
        return 0