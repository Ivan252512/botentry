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
                 
    def test_eval_function_with_genetic_algorithm(self):
        self.trader_bot.eval_function_with_genetic_algorithm()
        self.trader_bot.graph_data()