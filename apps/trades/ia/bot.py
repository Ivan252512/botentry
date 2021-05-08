from apps.trades.ia.basic_trading.trader import (
    TraderBTCBUSD
)

from apps.trades.ia.genetic_algorithm.ag import GeneticAlgorithm

from apps.trades.ia.utils.utils import (
    SimulateMarket
)



class TraderBot(object):
    def __init__(self):
        self.money = 0
        self.market = None
        self.periods = ['15m', '1h', '4h', '1d']
        self.trader_class = None
        self.traders_per_period = []
        
        
    def eval_function_with_genetic_algorithm(self):
            for p in self.periods:
                trader = self.trader_class(
                    _trading_interval=p,
                    _money=self.money
                )
                trader.prepare_data(_graphic=False)
                data = trader.graphic.get_processed_data()
                data_normalized = trader.graphic.get_normalized_processed_data()
                environment = data_normalized.values.tolist()
                
                # Market info
                self.market = SimulateMarket(
                    _data=data
                )
                
                # AG codification
                self.ag = GeneticAlgorithm(
                    _populations_quantity=12, 
                    _population_min=20, 
                    _population_max=100, 
                    _individual_dna_length=16, 
                    _individual_encoded_variables_quantity=len(environment[0]),
                    _individual_muatition_intensity=8,
                    _min_cod_ind_value=-10000,
                    _max_cod_ind_value=10000,
                    _environment=environment,
                )
                eval = self.ag.evolution(
                    _market=self.market, 
                    _initial_amount=self.money, 
                    _evaluation_intervals=4, 
                    _generations_pob=2,
                    _generations_ind=4
                )
                
                trader.graphic.process_data_received_ag(eval[2])
                self.traders_per_period.append(
                    {
                        'period': p,
                        'trader': trader
                    }
                )
    def graph_data(self):
        for t in self.traders_per_period:
            t['trader'].graphic.graph_for_ag()
        
class BTCBUSDTraderBot(TraderBot):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.money = 5000 
        self.trader_class = TraderBTCBUSD

        
        
