from apps.trades.ia.utils.utils import (
    SimulateBasicWallet,
    SimulateMarket
)


from apps.trades.binance.client import Client

from scipy.stats import linregress

from apps.trades.binance.exceptions import BinanceAPIException


class Individual:

    def __init__(self):
        self.relevant_info = []
        self.score = 0
        
    def add_relevant_info(self, _info):
        self.relevant_info.append(_info)

class BackTesting:
    def __init__(self, 
                 _environment,
                 _stop_loss_percent,
                 _stop_loss_divisor_plus, 
                 _keys,
                 _interval
                ):
        self.environment = _environment
        self.periods_environment = len(_environment)
        self.stop_loss_percent = _stop_loss_percent
        self.stop_loss_divisor_plus = _stop_loss_divisor_plus
        self.keys = _keys
        self.interval = _interval
        
    def test(self, _data):
          
        individual = Individual() 
        market = _data['market']
        initial_amount = _data['initial_amount']
        sl_percent = self.stop_loss_percent
        sl_divisor_plus = self.stop_loss_divisor_plus

        _wallet = SimulateBasicWallet()
        _wallet.deposit_coin_1(initial_amount)

        evaluation = self.__evaluate()
        for e in evaluation:
            if e["position_time"] < self.periods_environment:
                if e["buy"]:
                    # print(e)
                    coin_1_quantity = _wallet.get_balance_in_coin1()
                    if coin_1_quantity > 10:
                        coin_2_quantity, coin_2_price = market.transaction_at_moment_buy_coin2(
                            coin_1_quantity, e['position_time'])
                        if _wallet.buy_coin_2(coin_1_quantity, coin_2_quantity):
                            individual.add_relevant_info({
                                'coin_1_sell_quantity': coin_1_quantity,
                                'coin_2_buy_quantity': coin_2_quantity,
                                'coin_2_buy_price': coin_2_price,
                                'position_time': e['position_time'],
                                'balance_coin_1': _wallet.get_balance_in_coin1(),
                                'balance_coin_2': _wallet.get_balance_in_coin2(),
                                'stop_loss': [coin_2_price * (1 - sl_percent)]
                            })
                            #print("compra", individual.relevant_info)
                if e["sell"]:
                    coin_2_quantity = _wallet.get_balance_in_coin2()
                    if coin_2_quantity > 0:
                        coin_1_quantity_market, coin_2_price_market = market.transaction_at_moment_sell_coin2(
                            coin_2_quantity, e['position_time'])
                        # self.individual_relevant_info:
                        if _wallet.sell_coin_2(coin_1_quantity_market, coin_2_quantity):
                            individual.add_relevant_info({
                                'coin_1_buy_quantity': coin_1_quantity_market,
                                'coin_2_sell_quantity': coin_2_quantity,
                                'coin_2_sell_price': coin_2_price_market,
                                'position_time': e['position_time'],
                                'balance_coin_1': _wallet.get_balance_in_coin1(),
                                'balance_coin_2': _wallet.get_balance_in_coin2()
                            })
                else:
                    if len(individual.relevant_info) > 0 and "coin_1_sell_quantity" in individual.relevant_info[-1]:
                        _, coin_2_last_price_price = market.transaction_at_moment_sell_coin2(
                            0, e['position_time'])
                        sl = individual.relevant_info[-1]["stop_loss"][-1]
                        if coin_2_last_price_price < sl:
                            coin_2_quantity = _wallet.get_balance_in_coin2()
                            if coin_2_quantity > 0:
                                coin_1_quantity_market, coin_2_price_market = market.transaction_at_moment_sell_coin2(
                                    coin_2_quantity, e['position_time'])
                                # self.individual_relevant_info:
                                if _wallet.sell_coin_2(coin_1_quantity_market, coin_2_quantity):
                                    individual.add_relevant_info({
                                        'coin_1_buy_quantity': coin_1_quantity_market,
                                        'coin_2_sell_quantity': coin_2_quantity,
                                        'coin_2_sell_price': coin_2_price_market,
                                        'position_time': e['position_time'],
                                        'balance_coin_1': _wallet.get_balance_in_coin1(),
                                        'balance_coin_2': _wallet.get_balance_in_coin2()
                                    })
                                    #print("vende: ", individual.relevant_info)
                        else:
                            individual.relevant_info[-1]["stop_loss"].append(
                                individual.relevant_info[-1]["stop_loss"][-1] * (1 + (sl_divisor_plus)))
                            #print("aumenta stop loss: ", individual.relevant_info)
        total_earn = _wallet.get_total_balance_in_coin1(
            market.get_last_price())
        individual.score = total_earn if total_earn != initial_amount else -1
        return individual
    
    def __evaluate(self):
        to_test_2 = []
        position = 0
        interval = self.interval
        while position + interval  <= len(self.environment) - 1:
            var = {}
            for k in range(len(self.keys)):
                var[self.keys[k]] = []
                for se in self.environment[position:position+interval]:
                    var[self.keys[k]] += [se[k]]
            to_test_2.append(
                {
                    'position_time': position + interval,
                    'buy': self.MACD_strategy(var)[0],
                    'sell': self.MACD_strategy(var)[1],
                }
            )
            position += 1
            
        return to_test_2
    
    def buy_condition(self, value):
        self.MACD_strategy(value)
        return True
    
    def sell_condition(self, value):
        return False
    
    def MACD_strategy(self, value):
        macd = value.get('macd', None)
        signal = value.get('signal', None)
        histogram = value.get('histogram', None)
        ema_5 = value.get('ema_5', None)
        ema_10 = value.get('ema_10', None)
        ema_20 = value.get('ema_20', None)
        
        cross_macd = self.cross_variable(macd, signal)
        cross_ema_5_10 = self.cross_variable(ema_5, ema_20)
        cross_ema_10_20 = self.cross_variable(ema_10, ema_20)
        slope_histogram = self.slope(histogram)
        slope_ema_5 = self.slope(ema_5)
        slope_ema_10 = self.slope(ema_10)
        slope_ema_20 = self.slope(ema_20)
        
        buy_macd = False
        sell_macd = False
        if cross_ema_5_10 == 1:
            buy_macd = True
        elif cross_ema_5_10 == -1:
            sell_macd = True
            
        return buy_macd, sell_macd            

    def cross_variable(self, variable_1, variable_2):
        for i in range(len(variable_1)):       
            if variable_1[0] < variable_2[0]:
                if variable_1[i] >= variable_2[i]:
                    return 1
            else:
                if variable_1[i] <= variable_2[i]:
                    return -1
        return 0
    
    def slope(self, variable):
        t = [i for i in range(len(variable))]
        reg = linregress(
            x=t,
            y=variable
        )
        return reg[0] >= 0
class Strategy:
    
    def __init__(self, 
                 _principal_trade_period, 
                 _money, 
                 _sl_percent,
                 _sl_period,
                 _trader_class,
                 _pair,
                 _coin1,
                 _coin2,
                 _periods_environment,
                 _interval
        ):
        self.money = _money
        self.stop_loss_percent = _sl_percent
        self.stop_loss_divisor_plus = _sl_period
        self.market = None
        self.periods = ['15m', '1h', '4h', '1d']
        self.trader_class = _trader_class
        self.traders_per_period = []
        self.principal_trade_period = _principal_trade_period
        self.info_to_invest = {}
        self.client = Client()
        self.pair = _pair
        self.coin1 = _coin1
        self.coin2 = _coin2       
        self.periods_environment = _periods_environment 
        self.interval = _interval


    def eval_function_wit_last_individual(self):
        for p in self.periods:
            trader = self.trader_class(
                _trading_interval=p,
                _money=self.money
            )
            trader.prepare_data(_periods=self.periods_environment, _graphic=False)
            data = trader.graphic.get_processed_data()
            info = {}
            if p == self.principal_trade_period:
                environment = data.values.tolist()
                keys = data.keys()

                # Market info
                self.market = SimulateMarket(
                    _data=data
                )

                bt = BackTesting(
                    _environment=environment,
                    _stop_loss_percent=self.stop_loss_percent,
                    _stop_loss_divisor_plus=self.stop_loss_divisor_plus,
                    _keys=keys,
                    _interval=self.interval
                )


                data = {
                    "market": self.market,
                    "initial_amount": self.money,
                }
                
                best = bt.test(data)
                

                last_operation = trader.graphic.process_data_received_not_ai(
                    best.relevant_info,
                )

                self.info_to_invest = {
                    'score': best.score,
                    'operations': best.relevant_info,
                    'last_operation': last_operation
                }

            self.traders_per_period.append(
                {
                    'period': p,
                    'trader': trader,
                    'info': self.info_to_invest
                }
            )
            
    def graph_data(self):
        for t in self.traders_per_period:
            if t['info']:
                t['trader'].graphic.graph_for_evaluated_not_ai(
                    self.money, t['info']['score'], t['info']['last_operation'])
            t['trader'].graphic.graph()

    def invest(self):
        order = self.info_to_invest['last_operation']
        profit = self.info_to_invest['score']
        print("-------------------------------------------")
        print(order)
        print(profit)
        print("-------------------------------------------")
        if not "position_time" in order:
            return
        position_time = order['position_time']
        print("Position time: ", position_time)

        if 'coin_1_sell_quantity' in order:
            increase_sl = False
            buyed_price = 0
            try:
                if int(position_time) >= self.periods_environment - 2:
                    buy = self.buy_market(float(order["coin_2_buy_price"]))
                    if buy:
                        if buy["fills"]:
                            buyed_price = float(buy["fills"][-1]["price"])
            except BinanceAPIException as e:
                if e.code == -2010 and e.message == "Account has insufficient balance for requested action.":
                    self.increase_sl()
                    increase_sl = True
            finally:
                if int(position_time) >= self.periods_environment - 2:
                    if not increase_sl and buyed_price >= 0:
                        self.stop_loss_limit_sell(
                            float(buyed_price) * ( 1 - self.stop_loss_percent ),
                            float(buyed_price) * ( 1 - self.stop_loss_percent - 0.005 )
                        )
                else:
                    if not increase_sl:
                        self.increase_sl()    
        elif 'coin_2_sell_price' in order:
            # if int(position_time) == 498:
            #     self.stop_loss_limit_sell(
            #         float(ag_order["coin_2_sell_price"]),
            #         float(ag_order["coin_2_sell_price"]) * (1 - 0.005) 
            #     )
            # else:
            #     self.increase_sl()
            self.increase_sl()  
            
    def increase_sl(self):
        orders = self.get_open_orders()
        if orders:
            last_order = orders[-1]
            stop_price = float(last_order["stopPrice"]) * (1 + float(self.stop_loss_divisor_plus))
            price = stop_price * (1 - 0.005)
            self.stop_loss_limit_sell(
                float(stop_price),
                float(price)
            )

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
                print("BUY MARKET: ", self.pair, round(quantity, 4), quantity)
                buy = self.client.order_market_buy(
                    symbol=self.pair,
                    quantity=round(quantity, 4),
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
                print("SELL MARKET: ", self.pair, round(quantity, 4), quantity)
                sell = self.client.order_market_sell(
                    symbol=self.pair,
                    quantity=round(quantity, 4),
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
                print("BUY LIMIT: ", self.pair, round(quantity, 4), quantity, round(price, 2), price)
                buy = self.client.order_limit_buy(
                    symbol=self.pair,
                    quantity=round(quantity, 4),
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
                print("SL LIMIT: ", self.pair, round(quantity, 4), quantity, round(price, 2), price, round(stop, 2), stop)
                buy = self.client.order_limit_sell_stop_loss(
                    symbol=self.pair,
                    quantity=round(quantity, 4),
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