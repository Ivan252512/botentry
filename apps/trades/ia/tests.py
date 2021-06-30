from django.test import TestCase
from apps.trades.ia.bot import (
    BTCBUSDTraderBot, 
    ETHBUSDTraderBot,
    BNBBUSDTraderBot,
    ADABUSDTraderBot
)



import random

# Genetic Algorithm tests

class TraderBotCase:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trader_bot = None
        
    def setUp(self):
        pass
              
    def test_general(self):
        # self.trader_bot.set_info_to_invest()
        self.trader_bot.eval_function_with_genetic_algorithm()
        self.trader_bot.set_info_to_invest()
        self.trader_bot.graph_data()
        print("BUY MARKET TEST: ", self.trader_bot.buy_market(35000))

        
    # def test_get_all_orders(self):
    #     print("all_orders: ", self.trader_bot.get_all_orders())
    #     
    # def test_get_open_orders(self):
    #     print("open_orders: ", self.trader_bot.get_open_orders())
    #     
    # def test_get_order(self):
    #     print("order: ", self.trader_bot.get_order(_order_id=1795490356))
    #     
    # def test_get_coin1_balance(self):
    #     print("coin1 balance: ", self.trader_bot.get_coin1_balance())
    #     
    # def test_get_coin2_balance(self):
    #     print("coin2 balance: ", self.trader_bot.get_coin2_balance())
    #     
    # def test_get_average_price(self):
    #     print("price: ", self.trader_bot.get_last_average_price())
        
    # def test_buy(self):
    #     self.trader_bot.set_money(1)
    #     print(self.trader_bot.money)
    #     buy = self.trader_bot.buy()
    #     print("BUUUUUUUUUUUUY: {}".format(buy))
    
class BTCBUSDTraderBotCase(TraderBotCase, TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def setUp(self):
        super().setUp()
        self.trader_bot = BTCBUSDTraderBot(_principal_trade_period="15m")
        
# class ETHBUSDTraderBotCase(TraderBotCase, TestCase):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         
#     def setUp(self):
#         super().setUp()
#         self.trader_bot = ETHBUSDTraderBot(_principal_trade_period="15m")
#         
# 
# class BNBBUSDTraderBotCase(TraderBotCase, TestCase):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         
#     def setUp(self):
#         super().setUp()
#         self.trader_bot = BNBBUSDTraderBot(_principal_trade_period="15m")
#         
#         
# 
# class ADABUSDTraderBotCase(TraderBotCase, TestCase):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         
#     def setUp(self):
#         super().setUp()
#         self.trader_bot = ADABUSDTraderBot(_principal_trade_period="15m")     