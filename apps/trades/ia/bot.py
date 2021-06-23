from apps.trades.ia.basic_trading.trader import (
    TraderBTCBUSD,
    TraderETHBUSD,
    TraderADABUSD,
    TraderBNBBUSD,
    TraderBUSDUSDT
)

from apps.trades.ia.genetic_algorithm.ag import GeneticAlgorithm

from apps.trades.ia.utils.utils import (
    SimulateMarket
)

from apps.trades.binance.client import Client


class TraderBot(object):
    def __init__(self, _principal_trade_period):
        self.stop_loss = 0
        self.money = 5000
        self.market = None
        self.periods = ['15m', '1h', '4h', '1d']
        self.trader_class = None
        self.traders_per_period = []
        self.principal_trade_period =_principal_trade_period
        self.info_to_invest = {}
        self.client = Client()
        self.pair = None
        self.coin1 = None
        self.coin2 = None
        
        
    def eval_function_with_genetic_algorithm(self):
            for p in self.periods:
                trader = self.trader_class(
                    _trading_interval=p,
                    _money=self.money
                )
                trader.prepare_data(_graphic=False)
                data = trader.graphic.get_processed_data()
                ag = {}
                if p == self.principal_trade_period:
                    data_normalized = trader.graphic.get_normalized_processed_data()
                    environment = data_normalized.values.tolist()
                    
                    # Market info
                    self.market = SimulateMarket(
                        _data=data
                    )
                    
                    # AG codification
                    self.ag = GeneticAlgorithm(
                        _populations_quantity=1, 
                        _population_min=100, 
                        _population_max=500, 
                        _individual_dna_length=12, 
                        _individual_encoded_variables_quantity=len(environment[0]),
                        _individual_muatition_intensity=10,
                        _min_cod_ind_value=-1024,
                        _max_cod_ind_value=1024,
                        _environment=environment,
                    )
                    score, constants, operations = self.ag.evolution_individual_optimized(
                        _market=self.market, 
                        _initial_amount=self.money, 
                        _evaluation_intervals=4, 
                        _generations_pob=1,
                        _generations_ind=500
                    )
                    
                    last_operation = trader.graphic.process_data_received_ag(operations)
                    
                    ag = {
                        'score': score,
                        'constants': constants,
                        'operations': operations,
                        'last_operation': last_operation
                    }

                self.traders_per_period.append(
                    {
                        'period': p,
                        'trader': trader,
                        'ag': ag
                    }
                )
                
    def set_info_to_invest(self):
        info_15m = {}
        info_1h = {}
        info_4h = {}
        info_1d = {}
        for p in self.traders_per_period:
            if p['period'] == "15m":
                info_15m = p 
            elif p['period'] == "1h":
                info_1h = p 
            elif p['period'] == "4h":
                info_4h = p 
            elif p['period'] == "1d":
                info_1d = p 
        # Important variables
        ag_order = ""
        ag_profit = 0
        relevant_info = {
            "ma_7": 0,
            "ma_25": 0,
            "ma_99": 0,
            "fb_023": 0,
            "fb_038": 0,
            "fb_050": 0,
            "fb_061": 0,
            "fb_078": 0,
            "fb_100": 0,
            "fb_161": 0,
            "last_min_date": None,
            "last_min": None,
            "last_max_date": None,
            "last_max": None,
        }
                
        # 15m instructions
        if 'ag' in info_15m and info_15m['ag']:
            ag_order = info_15m['ag']['last_operation']
            ag_profit = info_15m['ag']['score']
        relevant_info_15m = relevant_info.copy()
        relevant_info_15m["ma_7"] = info_15m['trader'].graphic.get_last_ma_period(7)
        relevant_info_15m["ma_25"] = info_15m['trader'].graphic.get_last_ma_period(25)
        relevant_info_15m["ma_99"] = info_15m['trader'].graphic.get_last_ma_period(99)
        fibos = info_15m['trader'].graphic.get_fibos()
        relevant_info_15m["fb_023"] = fibos[0]
        relevant_info_15m["fb_038"] = fibos[1]
        relevant_info_15m["fb_050"] = fibos[2]
        relevant_info_15m["fb_061"] = fibos[3]
        relevant_info_15m["fb_078"] = fibos[4]
        relevant_info_15m["fb_100"] = fibos[5]
        relevant_info_15m["fb_161"] = fibos[6]
        min, min_index = info_15m['trader'].graphic.get_last_min_info()
        relevant_info_15m["last_min_date"] = min_index
        relevant_info_15m["last_min"] = min
        max, max_index = info_15m['trader'].graphic.get_last_max_info()
        relevant_info_15m["last_max_date"] = max_index
        relevant_info_15m["last_max"] = max
        # 1h instructions
        if 'ag' in info_1h and info_1h['ag']:
            ag_order = info_1h['ag']['last_operation']
            ag_profit = info_1h['ag']['score']
        relevant_info_1h = relevant_info.copy()
        relevant_info_1h["ma_7"] = info_1h['trader'].graphic.get_last_ma_period(7)
        relevant_info_1h["ma_25"] = info_1h['trader'].graphic.get_last_ma_period(25)
        relevant_info_1h["ma_99"] = info_1h['trader'].graphic.get_last_ma_period(99)
        fibos = info_1h['trader'].graphic.get_fibos()
        relevant_info_1h["fb_023"] = fibos[0]
        relevant_info_1h["fb_038"] = fibos[1]
        relevant_info_1h["fb_050"] = fibos[2]
        relevant_info_1h["fb_061"] = fibos[3]
        relevant_info_1h["fb_078"] = fibos[4]
        relevant_info_1h["fb_100"] = fibos[5]
        relevant_info_1h["fb_161"] = fibos[6]
        min, min_index = info_1h['trader'].graphic.get_last_min_info()
        relevant_info_1h["last_min_date"] = min_index
        relevant_info_1h["last_min"] = min
        max, max_index = info_1h['trader'].graphic.get_last_max_info()
        relevant_info_1h["last_max_date"] = max_index
        relevant_info_1h["last_max"] = max
        # 4h instructions
        if 'ag' in info_4h and info_4h['ag']:
            ag_order = info_4h['ag']['last_operation']
            ag_profit = info_4h['ag']['score']
        relevant_info_4h = relevant_info.copy()
        relevant_info_4h["ma_7"] = info_4h['trader'].graphic.get_last_ma_period(7)
        relevant_info_4h["ma_25"] = info_4h['trader'].graphic.get_last_ma_period(25)
        relevant_info_4h["ma_99"] = info_4h['trader'].graphic.get_last_ma_period(99)
        fibos = info_4h['trader'].graphic.get_fibos()
        relevant_info_4h["fb_023"] = fibos[0]
        relevant_info_4h["fb_038"] = fibos[1]
        relevant_info_4h["fb_050"] = fibos[2]
        relevant_info_4h["fb_061"] = fibos[3]
        relevant_info_4h["fb_078"] = fibos[4]
        relevant_info_4h["fb_100"] = fibos[5]
        relevant_info_4h["fb_161"] = fibos[6]
        min, min_index = info_4h['trader'].graphic.get_last_min_info()
        relevant_info_4h["last_min_date"] = min_index
        relevant_info_4h["last_min"] = min
        max, max_index = info_4h['trader'].graphic.get_last_max_info()
        relevant_info_4h["last_max_date"] = max_index
        relevant_info_4h["last_max"] = max
        # 1d instructions
        if 'ag' in info_1d and info_1d['ag']:
            ag_order = info_1d['ag']['last_operation']
            ag_profit = info_1d['ag']['score']
        relevant_info_1d = relevant_info.copy()
        relevant_info_1d["ma_7"] = info_1d['trader'].graphic.get_last_ma_period(7)
        relevant_info_1d["ma_25"] = info_1d['trader'].graphic.get_last_ma_period(25)
        relevant_info_1d["ma_99"] = info_1d['trader'].graphic.get_last_ma_period(99)
        fibos = info_1d['trader'].graphic.get_fibos()
        relevant_info_1d["fb_023"] = fibos[0]
        relevant_info_1d["fb_038"] = fibos[1]
        relevant_info_1d["fb_050"] = fibos[2]
        relevant_info_1d["fb_061"] = fibos[3]
        relevant_info_1d["fb_078"] = fibos[4]
        relevant_info_1d["fb_100"] = fibos[5]
        relevant_info_1d["fb_161"] = fibos[6]
        min, min_index = info_1d['trader'].graphic.get_last_min_info()
        relevant_info_1d["last_min_date"] = min_index
        relevant_info_1d["last_min"] = min
        max, max_index = info_1d['trader'].graphic.get_last_max_info()
        relevant_info_1d["last_max_date"] = max_index
        relevant_info_1d["last_max"] = max
    
        self.info_to_invest = {
            '15m': relevant_info_15m,
            '1h': relevant_info_1h,
            '4h': relevant_info_4h,
            '1d': relevant_info_1d,
            'ag_order': ag_order,
            'ag_profi': ag_profit
        }
    
        
    def decision_15m(self):
        info_15m = self.info_to_invest['15m']
    
    def decision_1h(self):
        info_1h = self.info_to_invest['1h']
    
    def decision_4h(self):
        info_4h = self.info_to_invest['4h']

    def decision_1d(self):
        info_1d = self.info_to_invest['1d']
        
    def set_money(self, _money):
        if float(self.get_coin1_balance()['free']) >= _money:
            self.money = _money
            return True
        return False
        
    def buy(self):
        price = float(self.get_last_average_price()['price'])
        buy = None
        if price > 0:
            quantity = self.money / price
            buy = self.client.order_market_buy(
                symbol=self.pair,
                quantity=quantity,
            )
        self.money = 0
        return buy
    
    def stop_loss_increment(self):
        pass
    
    def get_last_average_price(self):
        return self.client.get_avg_price(
            symbol=self.pair
        )
    
    def get_all_orders(self):
        return self.client.get_all_orders(
            symbol=self.pair
        )
        
    def get_open_orders(self):
        return self.client.get_open_orders(
            symbol=self.pair
        )
        
    def get_coin1_balance(self):
        return self.client.get_asset_balance(
            asset=self.coin1
        )
        
    def get_coin2_balance(self):
        return self.client.get_asset_balance(
            asset=self.coin2
        )
    
    def get_order(self, _order_id):
        return self.client.get_order(
            symbol=self.pair,
            orderId=_order_id
        )
        
                
    def graph_data(self):
        for t in self.traders_per_period:
            if t['ag']:
                t['trader'].graphic.graph_for_ag(self.money, t['ag']['score'], t['ag']['last_operation'])
            t['trader'].graphic.graph()   
        
class BTCBUSDTraderBot(TraderBot):
    def __init__(self, _principal_trade_period, *args, **kwargs):
        super().__init__(_principal_trade_period, *args, **kwargs)
        self.trader_class = TraderBTCBUSD
        self.pair = "BTCBUSD"
        self.coin1 = "BUSD"
        self.coin2 = "BTC"


class ETHBUSDTraderBot(TraderBot):
    def __init__(self, _principal_trade_period, *args, **kwargs):
        super().__init__(_principal_trade_period, *args, **kwargs)
        self.trader_class = TraderETHBUSD
        self.pair = "ETHBUSD"
        self.coin1 = "BUSD"
        self.coin2 = "ETH"
        
class ADABUSDTraderBot(TraderBot):
    def __init__(self, _principal_trade_period, *args, **kwargs):
        super().__init__(_principal_trade_period, *args, **kwargs)
        self.trader_class = TraderADABUSD
        self.pair = "ETHBUSD"
        self.coin1 = "BUSD"
        self.coin2 = "ETH"
        
class BNBBUSDTraderBot(TraderBot):
    def __init__(self, _principal_trade_period, *args, **kwargs):
        super().__init__(_principal_trade_period, *args, **kwargs)
        self.trader_class = TraderBNBBUSD
        self.pair = "ETHBUSD"
        self.coin1 = "BUSD"
        self.coin2 = "ETH"

        
        
