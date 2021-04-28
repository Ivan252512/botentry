
class SimulateBasicWallet:
    def __init__(self):
        self.__coin_1_balance = 0
        self.__coin_2_balance = 0
        
    def deposit(self, _quantity):
        if _quantity > 0:
            self.__coin_1_balance += _quantity
            return True
        return False
    
        
    def buy(self, _quantity):
        if _quantity > 0 and self.__coin_1_balance >= _quantity:
            self.__coin_1_balance -= _quantity
            return True
        return False
    
    def sell(self, _quantity):
        return self.deposit(_quantity)
    
    def get_balance(self):
        return self.__coin_1_balance
    
class SimulateMarket:
    def __init__(self, _data):
        self.data = _data 
        
    def sell_at_moment(self, quantity, moment):
        return "quantity in busd"
    
    def buy_at_moment(self, quantity, moment):
        return "quantity in btc"