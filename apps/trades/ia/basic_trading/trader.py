from apps.trades.binance.client import Client
from apps.trades.ia.utils.graphs.graphics import Graphic

class Trader:
    def __init__(self, _c1, _c2, _pair, _trading_interval, _money):
        self.client = Client()
        self.coin1 = _c1
        self.coin2 = _c2
        self.pair = _pair
        self.trading_interval = _trading_interval
        self.percent_wallet_assigned = _money
        self.graphic = None
        
    def get_account(self):
        return self.client.get_account()
    
    def get_pair_assets_balance(self):
        return {
            self.coin1: self.client.get_asset_balance(asset=self.coin1)["free"],
            self.coin2: self.client.get_asset_balance(asset=self.coin2)["free"]
        }

    def get_pair_klines_info(self, _periods):
        klines = self.client.get_klines(
            symbol=self.pair,
            limit=_periods,
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
    
    def get_all_orders(self):
        return self.client.get_all_orders(
            symbol=self.pair
        )
        
    def prepare_data(self, _periods, _graphic=True):
        klines = self.get_pair_klines_info(_periods)
        self.graphic = Graphic(
            _raw_data=klines, 
            _pair=self.pair, 
            _trading_interval=self.trading_interval
        )
        self.graphic.process_data()
        self.graphic.calculate_exponential_moving_average(_periods=5)
        self.graphic.calculate_exponential_moving_average(_periods=10)
        self.graphic.calculate_exponential_moving_average(_periods=20)
        self.graphic.calculate_exponential_moving_average(_periods=9, _graphic=False)
        self.graphic.calculate_exponential_moving_average(_periods=12, _graphic=False)
        self.graphic.calculate_exponential_moving_average(_periods=26, _graphic=False)
        self.graphic.get_cross_ma()
        self.graphic.get_cross_ema()
        self.graphic.calculate_macd()
        self.graphic.calculate_signal()
        self.graphic.calculate_histogram()
        # self.graphic.calculate_fibonacci_retracement()
        for i in range(3, 9, 3):
            self.graphic.get_second_derivative(_sigma_gaussian_filter=i)
        if _graphic:
            self.graphic.graph()
        
        
            
    
class TraderBUSDUSDT(Trader):
    
    def __init__(self, _trading_interval, _money, *args, **kwargs):
        super().__init__(
            _c1="BUSD",
            _c2="USDT",
            _pair="BUSDUSDT",
            _trading_interval=_trading_interval,
            _money=_money,
            *args, 
            **kwargs
        )
        
class TraderBTCBUSD(Trader):
    
    def __init__(self, _trading_interval, _money, *args, **kwargs):
        super().__init__(
            _c1="BTC",
            _c2="BUSD",
            _pair="BTCBUSD",
            _trading_interval=_trading_interval,
            _money=_money,
            *args, 
            **kwargs
        )
        
        
class TraderETHBUSD(Trader):
    
    def __init__(self, _trading_interval, _money, *args, **kwargs):
        super().__init__(
            _c1="ETH",
            _c2="BUSD",
            _pair="ETHBUSD",
            _trading_interval=_trading_interval,
            _money=_money,
            *args, 
            **kwargs
        )
        
class TraderBNBBUSD(Trader):
    
    def __init__(self, _trading_interval, _money, *args, **kwargs):
        super().__init__(
            _c1="BNB",
            _c2="BUSD",
            _pair="BNBBUSD",
            _trading_interval=_trading_interval,
            _money=_money,
            *args, 
            **kwargs
        )
        

class TraderADABUSD(Trader):
    
    def __init__(self, _trading_interval, _money, *args, **kwargs):
        super().__init__(
            _c1="ADA",
            _c2="BUSD",
            _pair="ADABUSD",
            _trading_interval=_trading_interval,
            _money=_money,
            *args, 
            **kwargs
        )
        
class TraderSHIBBUSD(Trader):
    
    def __init__(self, _trading_interval, _money, *args, **kwargs):
        super().__init__(
            _c1="SHIB",
            _c2="BUSD",
            _pair="SHIBBUSD",
            _trading_interval=_trading_interval,
            _money=_money,
            *args, 
            **kwargs
        )
        