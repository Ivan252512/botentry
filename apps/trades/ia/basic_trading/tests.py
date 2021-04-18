from django.test import TestCase

from apps.trades.ia.basic_trading.trader import (
    TraderBUSDUSDT
)
from apps.trades.binance.client import Client

import random

# Genetic Algorithm tests

class TraderBUSDUSDTTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trader = None
        
        
    def setUp(self):
        self.trader = TraderBUSDUSDT(_pwa=1)
                 
    def test_trader_created(self):
        self.assertEqual("BUSD", self.trader.coin1)
        self.assertEqual("USDT", self.trader.coin2)
        self.assertEqual("BUSDUSDT", self.trader.pair)
        self.assertIsInstance(self.trader.client, Client)
        
    def test_get_account(self):
        self.assertTrue(self.trader.get_account()["canTrade"])
        self.assertIsNotNone(self.trader.get_account()["balances"])
        
    def test_get_pair_assets_balance(self):
        balance = self.trader.get_pair_assets_balance()
        busd = float(balance["BUSD"])
        usdt = float(balance["USDT"])
        self.assertGreater(busd + usdt, 0)
        
    def test_get_pair_klines_info(self):
        self.trader.get_pair_klines_info()
        
    def test_visualization_klines(self):
        self.trader.visualization_klines()
        
    
        