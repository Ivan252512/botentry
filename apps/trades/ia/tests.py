from django.test import TestCase
from apps.trades.ia.bot import (
    BTCBUSDTraderBot
)



import random

# Genetic Algorithm tests

class BTCBUSDTraderBotCase(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trader_bot = None
        
    def setUp(self):
        self.trader_bot = BTCBUSDTraderBot(_principal_trade_period="15m")
        
                 
    # def test_general(self):
    #     self.trader_bot.eval_function_with_genetic_algorithm()
    #     self.trader_bot.set_info_to_invest()
    #     self.trader_bot.graph_data()
        
    def test_get_all_orders(self):
        print("all_orders: ", self.trader_bot.get_all_orders())
        
    def test_get_open_orders(self):
        print("open_orders: ", self.trader_bot.get_open_orders())
        
    def test_get_coin1_balance(self):
        print("coin1 balance: ", self.trader_bot.get_coin1_balance())
        
    def test_get_coin2_balance(self):
        print("coin2 balance: ", self.trader_bot.get_coin2_balance())