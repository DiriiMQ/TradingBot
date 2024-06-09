from symbol_st import Symbol
from enum import Enum
from abc import ABC, abstractmethod
import json

class Exchanger(Enum):
    HNX = 0
    HSX = 1
    UPCOM = 2
    BINANCE = 3

class ExchangerData(ABC):
    
    @abstractmethod
    def get_data(self, data_raw: list) -> list:
        pass


class HNXData(ExchangerData):
    def getNameAndSymbol(self, data: list) -> list:
        new_data = []
        for i in range(len(data)):
            if i % 3 == 1:
                new_data.append(data[i])
        return new_data

    def get_data(self, data_raw: list) -> list:
        data = []
        flag = False
        for i in data_raw:
            if '<select id="_txtcodename" style="width:300px">' in i:
                flag = True
                continue
            if flag:
                if '</select>' in i:
                    break
                data.append(i)

        data = self.getNameAndSymbol(data)
        for i in range(len(data)):
            data[i] = data[i].lstrip().split(' - ')
            data[i] = Symbol(data[i][0], "vietnam", "HNX")
        return data
    
class UPCOMData(ExchangerData):
    def getNameAndSymbol(self, data: list) -> list:
        new_data = []
        for i in range(len(data)):
            if i % 3 == 1:
                new_data.append(data[i])
        return new_data

    def get_data(self, data_raw: list) -> list:
        data = []
        flag = False
        for i in data_raw:
            if '<select id="_txtcodename" style="width:300px">' in i:
                flag = True
                continue
            if flag:
                if '</select>' in i:
                    break
                data.append(i)

        data = self.getNameAndSymbol(data)
        for i in range(len(data)):
            data[i] = data[i].lstrip().split(' - ')
            data[i] = Symbol(data[i][0], "vietnam", "UPCOM")
        return data

class HSXData(ExchangerData):
    def get_data(self, data_raw: list) -> list:
        data = []
        test = json.loads(''.join(data_raw))
        
        for i in test['rows']:
            data.append(Symbol(i['cell'][1], "vietnam", "HOSE"))

        return data
    
class BinanceData(ExchangerData):
    def get_data(self, data_raw: list) -> list:
        data = []
        symbols = []
        for i in data_raw:
            if i.endswith('USDT\n'):
                symbols.append(i.removesuffix('\n'))
        
        # symbols.append('USDT')
        symbols.sort()

        for i in symbols:
            data.append(Symbol(i, "crypto", "BINANCE"))

        return data

class DataExchangeCleaner:
    __exchangerFile = ['data/hnx_raw.txt', 'data/hsx_raw.txt', 'data/upcom_raw.txt', 'data/binance_symbols.txt']

    def __init__(self, exchanger: Exchanger, exchangerBot: ExchangerData) -> None:
        self.exchanger = exchanger
        self.symbols = []
        self.__data_raw = []
        self.data = []
        self.exchangerBot = exchangerBot

    def __read_file(self):
        with open(self.__exchangerFile[self.exchanger.value], 'r') as f:
            self.__data_raw = f.readlines()

    def run(self):
        self.__read_file()

        self.data = self.exchangerBot.get_data(self.__data_raw)
        return self
        
    def get_symbol(self, symbol: str) -> Symbol:
        for i in self.data:
            # print(i.symbol)
            if i.symbol == symbol:
                return Symbol(i.symbol, i.screener, i.exchange)
        return None