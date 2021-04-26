
class SimulateBasicWallet:
    def __init__(self):
        self.__balance = 0
        
    def deposit(self, _quantity):
        if _quantity > 0:
            self.__balance += _quantity
            return True
        return False
    
        
    def buy(self, _quantity):
        if _quantity > 0 and self.__balance >= _quantity:
            self.__balance -= _quantity
            return True
        return False
    
    def sell(self, _quantity):
        return self.deposit(_quantity)
    
    def get_balance(self):
        return self.__balance