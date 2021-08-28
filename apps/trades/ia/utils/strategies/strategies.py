from apps.trades.ia.utils.utils import (
    SimulateBasicWallet,
)



class Individual:

    def __init__(self):
        self.relevant_info = []
        self.evaluated_function = []
        
    def add_relevant_info(self, _info):
        self.relevant_info.append(_info)

class Strategy:
    def __init__(self, 
                 _environment,
                 _stop_loss_percent,
                 _stop_loss_divisor_plus, 
                ):
        self.environment = _environment
        self.periods_environment = len(_environment)
        self.stop_loss_percent = _stop_loss_percent
        self.stop_loss_divisor_plus = _stop_loss_divisor_plus
        
    def strategy(self, func, *args, **kwargs):
        return func(*args, **kwargs)
        
    def test(self, _data):
          
        individual = Individual() 
        market = _data['market']
        initial_amount = _data['initial_amount']
        evaluation_intervals = _data['evaluation_intervals']
        sl_percent = self.stop_loss_percent
        sl_divisor_plus = self.stop_loss_divisor_plus

        _wallet = SimulateBasicWallet()
        _wallet.deposit_coin_1(initial_amount)

        evaluation, = self.__evaluate(evaluation_intervals)
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
        score = total_earn if total_earn != initial_amount else -1
        return score
    
    def __evaluate(self, _evaluation_intervals):
        evaluated = []
        to_test_2 = []
        position = 0
        for temp in self.environment: 
            to_test_2.append(
                {
                    'position_time': position ,
                    'regresion_plus_1_val': regresion_plus_1_val,
                    'buy': self.__buy_condition(regresion_plus_1_val),
                    'sell': self.__sell_condition(regresion_plus_1_val),
                }
            )
        position += 1
            
        return to_test_2, evaluated
    
class CrossMA(Strategy):
    :