from apps.trades.binance.client import Client

class Trader:
    def __init__(self, _c1, _c2, _pair, _pwa):
        self.client = Client()
        self.coin1 = _c1
        self.coin2 = _c2
        self.pair = _pair
        self.trading_interval = "1m"
        self.percent_wallet_assigned = _pwa
        
    def get_account(self):
        return self.client.get_account()
    
    def get_pair_assets_balance(self):
        return {
            self.coin1: self.client.get_asset_balance(asset=self.coin1)["free"],
            self.coin2: self.client.get_asset_balance(asset=self.coin2)["free"]
        }

    def get_pair_klines_info(self):
        klines = self.client.get_klines(
            symbol=self.pair,
            interval=self.trading_interval
        )
        return klines
    
    def buy_coin1_sell_coin2(self, _quantity, _price):
        self.client.order_limit_buy(
            symbol=self.pair,
            quantity=_quantity,
            price=_price,
        )
        
    def buy_coin2_sell_coin1(self, _quantity, _price):
        self.client.order_limit_sell(
            symbol=self.pair,
            quantity=_quantity,
            price=_price,
        )
        
    def strategy_1(self):
        pass
            
    
class TraderBUSDUSDT(Trader):
    
    def __init__(self, _pwa, *args, **kwargs):
        super().__init__(
            _c1="BUSD",
            _c2="USDT",
            _pair="BUSDUSDT",
            _pwa=_pwa,
            *args, 
            **kwargs
        )
        
        
