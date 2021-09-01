from apps.trades.ia.utils.utils import (
    SimulateBasicWallet,
    SimulateMarket
)


from apps.trades.binance.client import Client



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
                ):
        self.environment = _environment
        self.periods_environment = len(_environment)
        self.stop_loss_percent = _stop_loss_percent
        self.stop_loss_divisor_plus = _stop_loss_divisor_plus
        
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
        for temp in self.environment: 
            to_test_2.append(
                {
                    'position_time': position,
                    'buy': self.buy_condition(temp),
                    'sell': self.sell_condition(temp),
                }
            )
            position += 1
            
        return to_test_2
    
    def buy_condition(self, value):
        return True
    
    def sell_condition(self, value):
        return False
    
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
                 _periods_environment
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
                data_normalized = trader.graphic.get_normalized_processed_data()
                environment = data_normalized.values.tolist()

                # Market info
                self.market = SimulateMarket(
                    _data=data
                )

                bt = BackTesting(
                    _environment=environment,
                    _stop_loss_percent=self.stop_loss_percent,
                    _stop_loss_divisor_plus=self.stop_loss_divisor_plus
                )


                data = {
                    "market": self.market,
                    "initial_amount": self.money,
                }
                
                best = bt.test(data)
                

                last_operation = trader.graphic.process_data_received_not_ai(
                    best.relevant_info,
                )

                info = {
                    'score': best.score,
                    'operations': best.relevant_info,
                    'last_operation': last_operation
                }

            self.traders_per_period.append(
                {
                    'period': p,
                    'trader': trader,
                    'info': info
                }
            )
            
    def graph_data(self):
        for t in self.traders_per_period:
            if t['info']:
                t['trader'].graphic.graph_for_evaluated_not_ai(
                    self.money, t['info']['score'], t['info']['last_operation'])
            t['trader'].graphic.graph()