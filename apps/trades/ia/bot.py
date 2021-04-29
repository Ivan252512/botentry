from apps.trades.ia.basic_trading.trader import (
    TraderBTCBUSD
)

from apps.trades.ia.genetic_algorithm.ag import GeneticAlgorithm

from apps.trades.ia.utils.utils import (
    SimulateBasicWallet,
    SimulateMarket
)


from abc import ABC, abstractmethod


class TraderBot(ABC):
    def __init__(self):
        self.pwa = 0
        self.market = None
        
    @abstractmethod
    def eval_function_with_genetic_algorithm(self, _period):
        pass
        
        
class BTCBUSDTraderBot(TraderBot):
    def __init__(self, _pwa, *args, **kwargs):
        super().__init__()
        self.pwa = _pwa 
        
    def eval_function_with_genetic_algorithm(self, _period):
        # Trader info
        trader = TraderBTCBUSD(
            _trading_interval=_period,
            _pwa=self.pwa
        )
        trader.prepare_data(_graphic=False)
        data = trader.graphic.get_processed_data()
        data_normalized = trader.graphic.get_normalized_processed_data()
        environment = data_normalized.values.tolist()
        
        # Market info
        self.market = SimulateMarket(
            _data=data,
            _price_column='open'
        )
        
        # Wallet
        wallet = SimulateBasicWallet()
        
        
        # AG codification
        self.ag = GeneticAlgorithm(
            _populations_quantity=1, 
            _population_min=20, 
            _population_max=100, 
            _individual_dna_length=20, 
            _individual_encoded_variables_quantity=len(environment[0]),
            _individual_muatition_intensity=5,
            _min_cod_ind_value=0,
            _max_cod_ind_value=100,
            _environment=environment,
        )
        self.ag.evolution(self.market, wallet, 10)
        
        
