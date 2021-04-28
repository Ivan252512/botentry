from apps.trades.ia.basic_trading.trader import (
    TraderBTCBUSD
)

from apps.trades.ia.genetic_algorithm.ag import GeneticAlgorithm

from apps.trades.ia.utils.utils import SimulateBasicWallet

from abc import ABC, abstractmethod


class TraderBot(ABC):
    def __init__(self):
        self.ag = None
        self.wallet = SimulateBasicWallet()
        self.pwa = 0
        self.trader = None
        
    @abstractmethod
    def eval_function_with_genetic_algorithm(self, _period):
        pass
        
        
class BTCBUSDTraderBot(TraderBot):
    def __init__(self, _pwa, *args, **kwargs):
        super().__init__()
        self.pwa = _pwa 
        
    def eval_function_with_genetic_algorithm(self, _period):
        data = self._set_trader('1d')
        environment = data.values.tolist()
        self.ag = GeneticAlgorithm(
            _populations_quantity=100, 
            _population_min=20, 
            _population_max=100, 
            _individual_dna_length=20, 
            _individual_encoded_variables_quantity=len(environment[0]),
            _individual_muatition_intensity=5,
            _min_cod_ind_value=0,
            _max_cod_ind_value=100,
            _environment=environment,
        )
        self.ag.evolution()
        
        
    def _set_trader(self, _period):
        trader = TraderBTCBUSD(
            _trading_interval=_period,
            _pwa=self.pwa
        )
        trader.prepare_data(_graphic=False)
        data = trader.graphic.get_normalized_processed_data()
        self.trader = trader
        return data
    
    def _fund(self, _wallet):
        total_disponible = self.trader.get_pair_assets_balance()['BUSD']
        self.wallet.deposit(total_disponible * self.pwa)
