import math


class SimulateBasicWallet:
    def __init__(self):
        self.__coin_1_balance = 0
        self.__coin_2_balance = 0

    def deposit_coin_1(self, _quantity):
        if _quantity > 0:
            self.__coin_1_balance += _quantity
            return True
        return False

    def buy_coin_2(self, _quantity_sell_coin_1, _quantity_buy_coin_2):
        if _quantity_sell_coin_1 > 0 and self.__coin_1_balance >= _quantity_sell_coin_1:
            self.__coin_1_balance -= _quantity_sell_coin_1
            self.__coin_2_balance += _quantity_buy_coin_2 * (1 - 0.001)
            return True
        return False

    def sell_coin_1(self, _quantity_sell_coin_1, _quantity_buy_coin_2):
        return self. buy_coin_2(_quantity_sell_coin_1, _quantity_buy_coin_2)

    def sell_coin_2(self, _quantity_buy_coin_1, _quantity_sell_coin_2):
        if _quantity_sell_coin_2 > 0 and self.__coin_2_balance >= _quantity_sell_coin_2:
            self.__coin_2_balance -= _quantity_sell_coin_2
            self.__coin_1_balance += _quantity_buy_coin_1 * (1 - 0.001)
            return True
        return False

    def buy_coin_1(self, _quantity_buy_coin_1, _quantity_sell_coin_2):
        return self.sell_coin_2(_quantity_buy_coin_1, _quantity_sell_coin_2)

    def get_total_balance_in_coin1(self, _change_value):
        return self.__coin_1_balance + self.__coin_2_balance * _change_value

    def get_total_balance_in_coin2(self, _change_value):
        return self.__coin_2_balance + self.__coin_1_balance * _change_value

    def get_balance_in_coin1(self):
        return self.__coin_1_balance

    def get_balance_in_coin2(self):
        return self.__coin_2_balance

    def get_all_balances(self):
        return {
            'coin_1': self.__coin_1_balance,
            'coin_2': self.__coin_2_balance
        }

    def restart(self):
        self.__coin_1_balance = 0
        self.__coin_2_balance = 0


class SimulateMarket:
    def __init__(self, _data):
        self.data = _data
        self.price_column_buy = "open"
        self.price_column_sell = "low"

    def transaction_at_moment_buy_coin2(self, quantity, moment):
        for t_price in self.data[self.price_column_buy]:
            if moment == 0:
                return quantity / t_price, t_price
            moment -= 1
        return 0, 0

    def transaction_at_moment_sell_coin2(self, quantity, moment):
        for t_price in self.data[self.price_column_sell]:
            if moment == 0:
                return quantity * t_price, t_price
            moment -= 1
        return 0, 0

    def get_last_price(self):
        return self.data[self.price_column_sell][-1]


def function_stop_loss(prices, sl_percent, sl_divisor):
    return prices[-1] * (1 + (sl_divisor))

class SimulateShort:
    def __init__(self):
        self.price_at_short = 0
        self.total_shorted = 0
        
    def short(self, _price_at_short, _total_shorted):
        self.__restart()
        self.price_at_short = _price_at_short
        self.total_shorted = _total_shorted
        
    def close(self, _price_at_close):
        total_at_open = self.price_at_short * self.total_shorted
        total_at_close = _price_at_close * self.total_shorted
        self.__restart()
        return total_at_close - total_at_open
    
    def __restart(self):
        self.price_at_short = 0
        self.total_shorted = 0
        