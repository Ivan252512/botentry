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
        self.trader_bot = BTCBUSDTraderBot(
            _pwa=10
        )
                 
    def test_eval_function_with_genetic_algorithm(self):
        self.trader_bot.eval_function_with_genetic_algorithm('1h')