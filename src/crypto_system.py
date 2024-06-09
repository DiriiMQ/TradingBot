import os, math, time
from binance.spot import Spot
from trading_system import TradingSystem
from clean_data import DataExchangeCleaner, Exchanger, BinanceData
from symbol_st import Symbol
from decision import DecisionStatus, DecisionSystem
from utils import bcolors

class CryptoSystem(TradingSystem): 
    def __init__(self):
        BINANCE_API_KEY = os.environ.get("BINANCE_TESTNET_API_KEY")
        BINANCE_SECRET_KEY = os.environ.get("BINANCE_TESTNET_SECRET_KEY")
        
        self.client = Spot(base_url='https://testnet.binance.vision', api_key=BINANCE_API_KEY, api_secret=BINANCE_SECRET_KEY)
        self.binance_dt = DataExchangeCleaner(Exchanger.BINANCE, BinanceData()).run()
        self.available_symbols = []
        self.all_symbols = self.binance_dt.data
        self.usdt = None
        self.resetTime = time.time()
        self.needReset = False
        self.INTERVAL_RESET = 0.00 # seconds
        self.GAP_TRANSACTION = 0.01 # seconds
    
    def initialize(self):
        acc = self.client.account()

        old_symbols = self.available_symbols
        self.available_symbols = []

        for i in acc['balances']:
            if float(i['free']) > 1e-9:
                # self.available_symbols.append(i['asset'])
                if i['asset'] == 'USDT':
                    symbol = Symbol(i['asset'], "crypto", "BINANCE")
                    symbol.availableAmount = float(i['free'])
                    self.usdt = symbol
                    continue

                # print(i['asset'])
                symbol = self.binance_dt.get_symbol(i['asset'] + 'USDT')
                if symbol is not None:
                    symbol.availableAmount = float(i['free'])
                    symbol.boughtPrice = float(self.client.ticker_price(symbol.symbol)['price'])
                    self.available_symbols.append(symbol)

                # set bought price for symbol at initialization is the current price
                # write a `update` function to update the available symbols and keep the bought price

        for i in old_symbols:
            for j in self.available_symbols:
                if i.symbol == j.symbol and i.boughtPrice > 0:
                    j.boughtPrice = i.boughtPrice
                    break
            
        return self
    
    def reset(self):
        if self.needReset:
            # time.sleep(self.GAP_TRANSACTION)
            # if time.time() - self.resetTime > self.INTERVAL_RESET:
            self.initialize()
            self.needReset = False
        pass
    
    def buy(self, symbol: str, quantity: float=1) -> None:
        self.reset()

        eth_price = self.client.ticker_price(symbol)['price']
        symbol_info = self.client.exchange_info(symbol) 

        step_size = float(symbol_info['symbols'][0]['filters'][1]['stepSize'])
        min_notional = float(symbol_info['symbols'][0]['filters'][6]['minNotional']) * 1.1
        needed_usdt = max(min_notional, quantity)
        buy_quantity = needed_usdt / float(eth_price)

        min_qty = float(symbol_info['symbols'][0]['filters'][1]['minQty'])
        buy_quantity = max(buy_quantity, min_qty)
        step10 = int(1 / step_size)

        if step10 % 9 == 0:
            step10 += 1

        # print('step10:', step10)
        # print('step_size:', step_size)

        buy_quantity = math.ceil(buy_quantity / step_size) / step10

        final_price = buy_quantity * float(eth_price)

        if self.usdt.availableAmount < needed_usdt:
            print("Not enough USDT")
            return

        try:
            print("Transaction:", bcolors.OKGREEN + 'BUY' + bcolors.ENDC, '-', symbol, "- at", eth_price, "- buy", buy_quantity, "- price", final_price)        
            order = self.client.new_order(symbol, 'BUY', 'MARKET', quantity=buy_quantity)
            flag = False
            for i in range(len(self.available_symbols)):
                if self.available_symbols[i].symbol == symbol:
                    if float(eth_price) > self.available_symbols[i].boughtPrice:
                        self.available_symbols[i].boughtPrice = float(eth_price)
                    self.available_symbols[i].availableAmount += buy_quantity
                    flag = True

            if not flag:
                symbol = Symbol(symbol, "crypto", "BINANCE")
                symbol.boughtPrice = float(eth_price)
                symbol.availableAmount = buy_quantity
                self.available_symbols.append(symbol)
            
            # print(order)
            if order['status'] == 'FILLED':
                print("Transaction success")
        except Exception as e:
            print("Error:", e)

        self.needReset = True
        self.resetTime = time.time()
        self.client.account()

        pass
    
    def sell(self, symbol: str, quantity: float=-1, forceSell: bool=False) -> None: # -1 means sell all
        self.reset()

        eth_price = self.client.ticker_price(symbol)['price']
        symbol_info = self.client.exchange_info(symbol)

        step_size = float(symbol_info['symbols'][0]['filters'][1]['stepSize'])
        min_notional = float(symbol_info['symbols'][0]['filters'][6]['minNotional'])
        min_qty = float(symbol_info['symbols'][0]['filters'][1]['minQty'])
        # print('min_qty:', min_qty)
        # print('step_size:', step_size)
        # print(min_notional)
        # max_qty = float(symbol_info['symbols'][0]['filters'][2]['maxQty'])
        
        for i in self.available_symbols:
            if i.symbol == symbol:
                if quantity == -1:
                    quantity = i.availableAmount

                if quantity > i.availableAmount:
                    print("Not enough", symbol)
                    return
                
                # print('step_size:', int(1 / step_size))

                step10 = int(1 / step_size)

                if step10 % 9 == 0:
                    step10 += 1
                
                # print('step10:', step10)
                # print('step_size:', step_size)
                # print('min_qty:', min_qty)
                # print('min_notional:', min_notional)

                sell_quantity = quantity
                sell_quantity = math.floor(sell_quantity / step_size) / step10

                final_price = sell_quantity * float(eth_price)

                # print('final_price:', final_price)

                if forceSell and (final_price < min_notional or sell_quantity < min_qty):
                    self.buy(symbol)
                    print(bcolors.WARNING + "Force buy" + bcolors.ENDC, symbol, "because of min_notional or min_qty")
                    print('NeedReset: ', self.needReset)
                    time.sleep(self.GAP_TRANSACTION)
                    self.sell(symbol)
                    return

                try: 
                    print("Transaction:", bcolors.FAIL + 'SELL' + bcolors.ENDC, '-', symbol, "- at", eth_price, "- sell", sell_quantity, "- price", final_price)
                    order = self.client.new_order(symbol, 'SELL', 'MARKET', quantity=sell_quantity)
                    # print(order)
                    if order['status'] == 'FILLED':
                        print("Transaction success")
                except Exception as e:
                    print("Error:", e)

                self.needReset = True
                self.resetTime = time.time()
                return

        print("Symbol not found")
        pass

    def get_in_available(self, symbol: str) -> Symbol:
        for i in self.available_symbols:
            if i.symbol == symbol:
                return i
        return None
    
    def run(self, desicionMaker: DecisionSystem) -> None:
        self.reset()

        for tsymbol in desicionMaker.get_potential_symbols():
            # print(tsymbol)
            if tsymbol[1] == 'USDT':
                continue
            
            flag = False
            for i in self.available_symbols:
                if i.symbol == tsymbol[1]:
                    flag = True
                    decision = desicionMaker.get_advice(i)
                    if decision == DecisionStatus.BUY:
                        self.buy(i.symbol)
                        time.sleep(self.GAP_TRANSACTION)
                    elif decision == DecisionStatus.SELL:
                        self.sell(i.symbol, forceSell=True)
                        time.sleep(self.GAP_TRANSACTION)
                    break

            if not flag:
                decision = desicionMaker.get_advice(self.binance_dt.get_symbol(tsymbol[1]))
                if decision == DecisionStatus.SELL:
                    print('Dont make sense to sell', tsymbol[1], 'because it is not in available symbols') 
                if decision == DecisionStatus.BUY:
                    self.buy(tsymbol[1])
                    time.sleep(self.GAP_TRANSACTION)
                    # continue

        self.initialize()
        for symbol in self.available_symbols:
            decision = desicionMaker.get_advice(symbol)
            if decision == DecisionStatus.SELL:
                self.sell(symbol.symbol, forceSell=True)
                time.sleep(self.GAP_TRANSACTION)
            # elif decision == DecisionStatus.BUY:
            #     self.buy(symbol.symbol)
            #     time.sleep(self.GAP_TRANSACTION)
    
    def loop(self, desicionMaker: DecisionSystem, minTrain: float=5) -> None:
        startTrain = time.time()
        while True:
            print("New loop")
            self.run(desicionMaker)

            if minTrain > 0 and time.time() - startTrain > minTrain * 60:
                break
            # time.sleep(60)
            pass
        self.sell_all()

    def calculate_up_to_date_balance(self) -> float:
        balance = self.usdt.availableAmount
        for i in self.available_symbols:
            balance += i.availableAmount * float(self.client.ticker_price(i.symbol)['price'])

        return balance

    def sell_all(self) -> None:
        print('SELL ALL AFTER TRAINING')
        for i in self.available_symbols:
            self.sell(i.symbol, forceSell=True)
            # time.sleep(self.GAP_TRANSACTION)
        pass
