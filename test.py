from vnstock import Vnstock
stock = Vnstock().stock(symbol='FPT', source='VCI')
result = stock.quote.history(start='2020-01-01', end='2024-05-25')
print(result.to_csv())