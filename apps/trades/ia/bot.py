from apps.trades.binance.exceptions import BinanceAPIException
from apps.trades.ia.basic_trading.trader import (
    TraderBTCBUSD,
    TraderETHBUSD,
    TraderADABUSD,
    TraderBNBBUSD,
    TraderBUSDUSDT
)

from apps.trades.models import Individual as IndividualModel
from apps.trades.models import Trade as TradeModel


from apps.trades.ia.genetic_algorithm.ag import GeneticAlgorithm

from apps.trades.ia.genetic_algorithm.ag import Individual as IndividualAG

from apps.trades.ia.utils.utils import (
    SimulateMarket,
    function_stop_loss
)

from apps.trades.binance.client import Client

import traceback


class TraderBot(object):
    def __init__(self, 
                 _principal_trade_period, 
                 _money, 
                 _sl_percent,
                 _sl_period,
                 _population_min,
                 _population_max,
                 _individual_dna_length,
                 _individual_muatition_intensity,
                 _min_cod_ind_value,
                 _max_cod_ind_value,
                 _generations_ind
        ):
        self.money = _money
        self.stop_loss_percent = _sl_percent
        self.stop_loss_divisor_plus = _sl_period
        self.market = None
        self.periods = ['15m', '1h', '4h', '1d']
        self.trader_class = None
        self.traders_per_period = []
        self.principal_trade_period = _principal_trade_period
        self.info_to_invest = {}
        self.client = Client()
        self.pair = None
        self.coin1 = None
        self.coin2 = None
        self.population_min = _population_min
        self.population_max = _population_max
        self.individual_dna_length = _individual_dna_length
        self.individual_muatition_intensity = _individual_muatition_intensity
        self.min_cod_ind_value = _min_cod_ind_value
        self.max_cod_ind_value = _max_cod_ind_value
        self.generations_ind = _generations_ind
        

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
                    _population_min=self.population_min,
                    _population_max=self.population_max,
                    _individual_dna_length=self.individual_dna_length,
                    _individual_encoded_variables_quantity=len(environment[0]),
                    _individual_muatition_intensity=self.individual_muatition_intensity,
                    _min_cod_ind_value=self.min_cod_ind_value,
                    _max_cod_ind_value=self.max_cod_ind_value,
                    _environment=environment,
                    _stop_loss_percent=self.stop_loss_percent,
                    _stop_loss_divisor_plus=self.stop_loss_divisor_plus
                )
                score, constants, operations, best = self.ag.evolution_individual_optimized(
                    _market=self.market,
                    _initial_amount=self.money,
                    _evaluation_intervals=4,
                    _generations_pob=1,
                    _generations_ind=self.generations_ind
                )

                IndividualModel.objects.create(
                    length=best.length,
                    encoded_variables_quantity=best.encoded_variables_quantity,
                    mutation_intensity=best.mutation_intensity,
                    dna=best.dna,
                    score=best.score,
                    min_value=best.min_value,
                    max_value=best.max_value,
                    pair=self.pair,
                    temp=self.principal_trade_period,
                    percent=self.stop_loss_percent,
                    percent_divisor_increment=self.stop_loss_divisor_plus
                )

                last_operation = trader.graphic.process_data_received_ag(
                    operations)

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

    def eval_function_with_genetic_algorithm_last_individual(self):
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
                    _population_min=self.population_min,
                    _population_max=self.population_max,
                    _individual_dna_length=self.individual_dna_length,
                    _individual_encoded_variables_quantity=len(environment[0]),
                    _individual_muatition_intensity=self.individual_muatition_intensity,
                    _min_cod_ind_value=self.min_cod_ind_value,
                    _max_cod_ind_value=self.max_cod_ind_value,
                    _environment=environment,
                    _stop_loss_percent=self.stop_loss_percent,
                    _stop_loss_divisor_plus=self.stop_loss_divisor_plus
                )

                ind_model_object = IndividualModel.objects.filter(
                    length=self.individual_dna_length,
                    encoded_variables_quantity=len(environment[0]),
                    min_value=self.min_cod_ind_value,
                    max_value=self.max_cod_ind_value,
                    pair=self.pair,
                    temp=self.principal_trade_period,
                    percent=self.stop_loss_percent,
                    percent_divisor_increment=self.stop_loss_divisor_plus
                ).last()

                individual = IndividualAG(
                    _length=ind_model_object.length,
                    _encoded_variables_quantity=ind_model_object.encoded_variables_quantity,
                    _mutation_intensity=ind_model_object.mutation_intensity,
                    _min_value=ind_model_object.min_value,
                    _max_value=ind_model_object.max_value,
                    _dna=ind_model_object.dna
                )

                data = {
                    "market": self.market,
                    "initial_amount": self.money,
                    "evaluation_intervals": 4,
                    "individual": individual
                }

                best = self.ag.optimized_individual_function(
                    _data=data
                )

                last_operation = trader.graphic.process_data_received_ag(
                    best.relevant_info)

                ag = {
                    'score': best.score,
                    'constants': best.decode_dna_variables_to_decimal(),
                    'operations': best.relevant_info,
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
        relevant_info_15m["ma_7"] = info_15m['trader'].graphic.get_last_ma_period(
            7)
        relevant_info_15m["ma_25"] = info_15m['trader'].graphic.get_last_ma_period(
            25)
        relevant_info_15m["ma_99"] = info_15m['trader'].graphic.get_last_ma_period(
            99)
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
        relevant_info_1h["ma_7"] = info_1h['trader'].graphic.get_last_ma_period(
            7)
        relevant_info_1h["ma_25"] = info_1h['trader'].graphic.get_last_ma_period(
            25)
        relevant_info_1h["ma_99"] = info_1h['trader'].graphic.get_last_ma_period(
            99)
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
        relevant_info_4h["ma_7"] = info_4h['trader'].graphic.get_last_ma_period(
            7)
        relevant_info_4h["ma_25"] = info_4h['trader'].graphic.get_last_ma_period(
            25)
        relevant_info_4h["ma_99"] = info_4h['trader'].graphic.get_last_ma_period(
            99)
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
        relevant_info_1d["ma_7"] = info_1d['trader'].graphic.get_last_ma_period(
            7)
        relevant_info_1d["ma_25"] = info_1d['trader'].graphic.get_last_ma_period(
            25)
        relevant_info_1d["ma_99"] = info_1d['trader'].graphic.get_last_ma_period(
            99)
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
            'ag_profit': ag_profit
        }

    def invest_based_ag(self):
        ag_order = self.info_to_invest['ag_order']
        ag_profit = self.info_to_invest['ag_profit']
        print("-------------------------------------------")
        print(ag_order)
        print(ag_profit)
        print("-------------------------------------------")
        if not "position_time" in ag_order:
            return
        position_time = ag_order['position_time']
        print("Position time: ", position_time)

        if 'coin_1_sell_quantity' in ag_order:
            increase_sl = False
            buyed_price = 0
            try:
                if int(position_time) == 499:
                    buy = self.buy_market(float(ag_order["coin_2_buy_price"]))
                    if buy:
                        if buy["fills"]:
                            buyed_price = float(buy["fills"][-1]["price"])
            except BinanceAPIException as e:
                if e.code == -2010 and e.message == "Account has insufficient balance for requested action.":
                    self.increase_sl()
                    increase_sl = True
            finally:
                if int(position_time) == 499:
                    if not increase_sl and buyed_price >= 0:
                        self.stop_loss_limit_sell(
                            float(buyed_price) * ( 1 - self.stop_loss_percent ),
                            float(buyed_price) * ( 1 - self.stop_loss_percent - 0.005 )
                        )
                else:
                    if not increase_sl:
                        self.increase_sl()    
        elif 'coin_2_sell_price' in ag_order:
            if int(position_time) == 499:
                self.stop_loss_limit_sell(
                    float(ag_order["coin_2_sell_price"]),
                    float(ag_order["coin_2_sell_price"]) * (1 - 0.005) 
                )
            else:
                self.increase_sl()  
                
    def increase_sl(self):
        orders = self.get_open_orders()
        if orders:
            last_order = orders[-1]
            stop_price = float(last_order["stopPrice"]) * (1 + float(self.stop_loss_percent)/float(self.stop_loss_divisor_plus))
            price = stop_price * (1 - 0.005)
            self.stop_loss_limit_sell(
                float(stop_price),
                float(price)
            )


    def decision_15m(self):
        info_15m = self.info_to_invest['15m']

    def decision_1h(self):
        info_1h = self.info_to_invest['1h']

    def decision_4h(self):
        info_4h = self.info_to_invest['4h']

    def decision_1d(self):
        info_1d = self.info_to_invest['1d']

    def cancel_all_open_orders(self):
        for oo in self.get_open_orders():
            if oo["symbol"] == self.pair:
                self.cancel_order(oo["orderId"])

    def cancel_order(self, order_id):
        self.client.cancel_order(
            symbol=self.pair,
            orderId=order_id
        )

    def set_money(self, _money):
        if float(self.get_coin1_balance()['free']) >= _money:
            self.money = _money
            return True
        return False

    def buy_market(self, price):
        print("BUY MARKET PRICE: ", price)
        buy = None
        if price > 0:
            exception = ""
            quantity = 0
            traceback_str = ""
            try:
                quantity = self.money / price
                print("BUY MARKET: ", self.pair, round(quantity, 6), quantity)
                buy = self.client.order_market_buy(
                    symbol=self.pair,
                    quantity=round(quantity, 6),
                )
            except Exception as e:
                exception = str(e)
                traceback_str = traceback.format_exc()
                raise e
            finally:
                TradeModel.objects.create(
                    pair=self.pair,
                    operation="BUY MARKET",
                    money=self.money,
                    price=price,
                    quantity=quantity,
                    error=exception,
                    traceback=traceback_str
                )
        return buy

    def sell_market(self, price):
        print("SELL MARKET PRICE: ", price)
        sell = None
        if price > 0:
            exception = ""
            quantity = 0
            traceback_str = ""
            try:
                quantity = self.money / price
                print("SELL MARKET: ", self.pair, round(quantity, 6), quantity)
                sell = self.client.order_market_sell(
                    symbol=self.pair,
                    quantity=round(quantity, 6),
                )
            except Exception as e:
                exception = str(e)
                traceback_str = traceback.format_exc()
                raise e
            finally:
                TradeModel.objects.create(
                    pair=self.pair,
                    operation="SELL MARKET",
                    money=self.money,
                    price=price,
                    quantity=quantity,
                    error=exception,
                    traceback=traceback_str
                )
        return sell

    def buy_limit(self, price):
        print("BUY LIMIT PRICE: ", price)
        buy = None
        if price > 0:
            exception = ""
            quantity = 0
            traceback_str = ""
            try:
                quantity = self.money / price
                print("BUY LIMIT: ", self.pair, round(quantity, 6), quantity, round(price, 2), price)
                buy = self.client.order_limit_buy(
                    symbol=self.pair,
                    quantity=round(quantity, 6),
                    price=round(price, 2)
                )
            except Exception as e:
                exception = str(e)
                traceback_str = traceback.format_exc()
                raise e
            finally:
                TradeModel.objects.create(
                    pair=self.pair,
                    operation="BUY LIMIT",
                    money=self.money,
                    price=price,
                    quantity=quantity,
                    error=exception,
                    traceback=traceback_str
                )
        return buy

    def stop_loss_limit_sell(self, stop, price):
        self.cancel_all_open_orders()
        print("SL LIMIT PRICE: ", price)
        buy = None
        if price > 0 and stop > 0:
            exception = ""
            quantity = 0
            traceback_str = ""
            try:
                quantity = self.money / price
                print("SL LIMIT: ", self.pair, round(quantity, 6), quantity, round(price, 2), price, round(stop, 2), stop)
                buy = self.client.order_limit_sell_stop_loss(
                    symbol=self.pair,
                    quantity=round(quantity, 6),
                    price=round(price, 2),
                    stopPrice=round(stop, 2)
                )
            except BinanceAPIException as e:
                if e.code == -2010 and e.message == "Stop price would trigger immediately.":
                        self.sell_market(
                            float(round(stop, 2))
                        )
                exception = str(e)
                traceback_str = traceback.format_exc()
                raise e
            except Exception as e:
                exception = str(e)
                traceback_str = traceback.format_exc()
                raise e
            finally:
                TradeModel.objects.create(
                    pair=self.pair,
                    operation="SL LIMIT",
                    money=self.money,
                    price=price,
                    quantity=quantity,
                    error=exception,
                    traceback=traceback_str
                )
        return buy

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
                t['trader'].graphic.graph_for_ag(
                    self.money, t['ag']['score'], t['ag']['last_operation'])
            t['trader'].graphic.graph()


class BTCBUSDTraderBot(TraderBot):
    def __init__(self, 
                 _principal_trade_period, 
                 _money, 
                 _sl_percent,
                 _sl_period,
                 _population_min,
                 _population_max,
                 _individual_dna_length,
                 _individual_muatition_intensity,
                 _min_cod_ind_value,
                 _max_cod_ind_value,
                 _generations_ind,
                 *args, 
                 **kwargs
        ):
        super().__init__(
            _principal_trade_period, 
            _money,
            _sl_percent,
            _sl_period,
            _population_min,
            _population_max,
            _individual_dna_length,
            _individual_muatition_intensity,
            _min_cod_ind_value,
            _max_cod_ind_value,
            _generations_ind, 
            *args, 
            **kwargs
        )
        self.trader_class = TraderBTCBUSD
        self.pair = "BTCBUSD"
        self.coin1 = "BUSD"
        self.coin2 = "BTC"


class ETHBUSDTraderBot(TraderBot):
    def __init__(self, _principal_trade_period, _sl_percent, _sl_period, *args, **kwargs):
        super().__init__(_principal_trade_period, _sl_percent, _sl_period, *args, **kwargs)
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
