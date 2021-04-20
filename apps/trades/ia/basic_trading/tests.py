from django.test import TestCase

from apps.trades.ia.basic_trading.trader import (
    TraderBUSDUSDT,
    TraderBTCBUSD
)
from apps.trades.binance.client import Client


import random

# Genetic Algorithm tests

class TraderPair():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trader = None
        self.coin1 = None
        self.coin2 = None
        self.pair = None
        
    def setUp(self):
        pass
        
    def test_son_class(self):
        print("Running for class, {}.".format(self.__class__))
                 
    def test_trader_created(self):
        self.assertEqual(self.coin1, self.trader.coin1)
        self.assertEqual(self.coin2, self.trader.coin2)
        self.assertEqual(self.pair, self.trader.pair)
        self.assertIsInstance(self.trader.client, Client)
        
    def test_get_account(self):
        self.assertTrue(self.trader.get_account()["canTrade"])
        self.assertIsNotNone(self.trader.get_account()["balances"])
        
    def test_get_pair_assets_balance(self):
        balance = self.trader.get_pair_assets_balance()
        busd = float(balance[self.coin1])
        usdt = float(balance[self.coin2])
        self.assertGreater(busd + usdt, 0)
        
    def test_get_pair_klines_info(self):
        self.trader.get_pair_klines_info()
        
    def test_visualization_klines(self):
        self.trader.visualization_klines()
        

class TraderBUSDUSDTTestCase(TraderPair, TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coin1 = "BUSD"
        self.coin2 = "USDT"
        self.pair = "BUSDUSDT"
        
    def setUp(self):
        super().setUp()
        self.trader = TraderBUSDUSDT(_pwa=1)

class TraderBTCBUSDTestCase(TraderPair, TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coin1 = "BTC"
        self.coin2 = "BUSD"
        self.pair = "BTCBUSD"
        
    def setUp(self):
        super().setUp()
        self.trader = TraderBTCBUSD(_pwa=1)

        
        
