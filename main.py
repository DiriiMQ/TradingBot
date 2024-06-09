# from src.clean_data import DataExchangeCleaner, Exchanger, HNXData, UPCOMData, HSXData, BinanceData
# from src.strategies import NPN_Maker

# hnx = DataExchangeCleaner(Exchanger.HNX, HNXData()).run()
# upcom = DataExchangeCleaner(Exchanger.UPCOM, UPCOMData()).run()
# hsx = DataExchangeCleaner(Exchanger.HSX, HSXData()).run()
# binance = DataExchangeCleaner(Exchanger.BINANCE, BinanceData()).run()

# npn = NPN_Maker().initialize(binance.data)
# print(binance.data)

import os
from dotenv import load_dotenv
from src.crypto_system import CryptoSystem
from src.strategies import NPN_Maker

from src.utils import TradingView_TA, Interval
from src.symbol_st import Symbol

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

crypto = CryptoSystem()
crypto.initialize()
# for i in crypto.available_symbols:
#     if i.symbol == "ETHUSDT":
#         print(i)

print(crypto.usdt)

pre_train = crypto.calculate_up_to_date_balance()

winner = NPN_Maker().initialize(crypto.all_symbols) # decision system
crypto.loop(winner, 3)

post_train = crypto.calculate_up_to_date_balance()
print('Pre-train:', pre_train, 'USDT')
print('Post-train:', post_train, 'USDT')
print('Rate profit:', (post_train - pre_train) / pre_train * 100, '%')

# crypto.sell('MDXUSDT')
