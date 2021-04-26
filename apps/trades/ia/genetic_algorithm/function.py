from apps.trades.ia.basic_trading.trader import (
    TraderBTCBUSD
)

from apps.trades.ia.genetic_algorithm.ag import GeneticAlgorithm

from apps.trades.ia.utils.utils import SimulateBasicWallet

from abc import ABC, abstractmethod


class TraderFunction(ABC):
    def __init__(self):
        self.ag = GeneticAlgorithm()
        self.wallet = SimulateBasicWallet()
        self.pwa = 0
        self.trader = None
        
    @abstractmethod
    def eval_function_only_one_period(self, _period):
        pass
        
        
class BTCBUSDTraderFunction(TraderFunction):
    def __init__(self, _pwa, *args, **kwargs):
        super().__init__()
        self.pwa = _pwa 
        
    def eval_function_only_one_period(self, _period):
        """Evaluation function for genetic algorithm, receives Graphic data, process the like a time series and return the earn,
        earnest is the fittest"""
        data = self._set_trader(_period)
        
        
    def eval_function_n_periods(self, _periods):
        pass
        
    def _set_trader(self, _period):
        trader = TraderBTCBUSD(
            _trading_interval=_period,
            _pwa=self.pwa
        )
        trader.prepare_data(_graphic=False)
        data = trader.graphic.get_processed_data()
        self.trader = trader
        return data
    
    def _fund(self):
        total_disponible = self.trader.get_pair_assets_balance()['BUSD']
        self.wallet.deposit(total_disponible * self.pwa)
        
        