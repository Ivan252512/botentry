
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
            self.__coin_2_balance += _quantity_buy_coin_2
            return True
        return False
    
    def sell_coin_1(self, _quantity_sell_coin_1, _quantity_buy_coin_2):
        return self. buy_coin_2(_quantity_sell_coin_1, _quantity_buy_coin_2)
    
    def sell_coin_2(self, _quantity_buy_coin_1, _quantity_sell_coin_2):
        if _quantity_sell_coin_2 > 0 and self.__coin_2_balance >= _quantity_sell_coin_2:
            self.__coin_2_balance -= _quantity_sell_coin_2
            self.__coin_1_balance += _quantity_buy_coin_1
            return True
        return False
    
    def buy_coin_1(self, _quantity_buy_coin_1, _quantity_sell_coin_2):
        return self.sell_coin_2(_quantity_buy_coin_1, _quantity_sell_coin_2)
    
    def get_total_balance_in_coin1(self, _change_value):
        return self.__coin_1_balance + self.__coin_2_balance * _change_value
    
    def get_total_balance_in_coin2(self, _change_value):
        return self.__coin_2_balance + self.__coin_1_balance * _change_value
    
    def restart(self):
        self.__coin_1_balance = 0
        self.__coin_2_balance = 0
    
    
    
class SimulateMarket:
    def __init__(self, _data, _price_column='open'):
        self.data = _data 
        self.price_column = _price_column
        
    def transaction_at_moment(self, quantity, moment):
        for t in self.data[self.price_column]:
            if moment == 0:
                return t * quantity
            moment -= 1
        return 0