import numpy as np
import random
from multiprocessing.pool import ThreadPool

from scipy.stats import linregress

# Genetic algorithm

class Individual:
    
    def __init__(self, 
                 _length,
                 _encoded_variables_quantity,
                 _mutation_intensity, 
                 _min_value,
                 _max_value,
                 _dna=None
        ):
        self.length = _length
        self.encencoded_variables_quantity = _encoded_variables_quantity
        self.mutation_intensity = random.randint(1, _mutation_intensity)
        self.dna = _dna if _dna else self.generate_individual() 
        self.score = 0
        self.min_value = _min_value
        self.max_value = _max_value
        
    def generate_individual(self):
        """Generate n bits strings individual
        
        :param nbits: String length simulating the bits quantity
        :type nbits: int
        
        """ 
        count = 0
        individual = ""
        all_dna_length = self.length * self.encencoded_variables_quantity
        while(count<all_dna_length):
            individual += str(random.randint(0, 1))
            count += 1 
        return individual
    
    def decode_dna_variables_to_decimal(self):
        dnas = self._cut_dna(self.dna, self.length)
        decoded_variables = []
        for gen in dnas:
            decoded_variables.append(
                self._binary_to_decimal(gen)
            )
        return decoded_variables
    
    def _binary_to_decimal(self, gen):
        """ Converts binary values into a decimal values with one comma, between 
        [a,b] interval
        
        :param bin: String binary value
        :type bin: String:
        :param a: Start interval
        :type a: int
        :param b: End interval
        :type b: int
        """
        a=self.min_value
        b=self.max_value
        n_count = len(gen)
        n = n_count
        dec = 0
        for i in gen:
            if i=='1':
                dec+=2**(n_count-1)
            n_count-=1
        return  a+((dec)/(2**n-1))*(b-a)
    
    def _cut_dna(self, dna, len_interval):
        if len(dna) % len_interval:
            raise Exception("The length of dna must be multiple of len_interval ")
        if len(dna) == len_interval:
            return [dna]
        return [dna[:len_interval]] + self._cut_dna(dna[len_interval:], len_interval)
        
    
    def mutation(self):
        bin = list(self.dna)
        for _ in range(int(len(bin)/random.randint(1, self.mutation_intensity))):
            rand=random.randint(0, self.length - 1)
            if(bin[rand]=="0"):
                bin[rand]="1"
            if(bin[rand]=="1"):
                bin[rand]="0"
        return "".join(bin)

    def set_score(self, _score):
        self.score = _score
        



class Population:
    
    def __init__(self, 
                 _quantity,
                 _encoded_variables_quantity,
                 _dna_length, 
                 _mutation_intensity, 
                 _min_cod_ind_value,
                 _max_cod_ind_value
        ):
        self.quantity = _quantity
        self.dna_length = _dna_length
        self.encoded_variables_quantity = _encoded_variables_quantity
        self.mutation_intensity = _mutation_intensity
        self.min_cod_ind_value=_min_cod_ind_value
        self.max_cod_ind_value=_max_cod_ind_value
        self.score = 0
        self.population = self.generate_population()
    
    def generate_population(self):
        population = []
        count = 0
        while(count < self.quantity):
            individual = Individual(
                _length=self.dna_length, 
                _encoded_variables_quantity =self.encoded_variables_quantity,
                _mutation_intensity=self.mutation_intensity,
                _min_value=self.min_cod_ind_value,
                _max_value=self.max_cod_ind_value
            )
            population.append(individual)
            count += 1
        return population
            
    def breed(self):
        """
        Reproduction function, cross the gen for two individuals, uniform cross.
        :param bin1: One individual
        """
        self.__order_by_individual_score()
        half = int(self.quantity/2)
        best_half = self.population[:half]
        ten_percent = int(self.quantity/10)
        best_ten_percent = self.population[:ten_percent]
        
        
        new_population = []
        for _ in range(half * 2):
            mother = best_ten_percent[random.randint(0, ten_percent - 1)].dna
            father = best_half[random.randint(0, half - 1)].dna
            new_population.append(
                self.__cross_genes(
                    father,
                    mother
                )
            )
            
        current_generation = best_ten_percent
        new_quantity = self.quantity - len(current_generation)
        while new_quantity > 0:
            current_generation.append(new_population[new_quantity])
            new_quantity -= 1
            
            
    def __order_by_individual_score(self):
        self.population.sort(key=lambda individual: individual.score)

    def __cross_genes(self, father, mother):
        son_dna = ""
        for i in range(self.dna_length):
            rand=random.randint(0,1)
            if (rand==0):
                son_dna += father[i]
            else:
                son_dna += mother[i]
        son = Individual(
                _length=self.dna_length,
                _encoded_variables_quantity=self.encoded_variables_quantity,
                _mutation_intensity=self.mutation_intensity,
                _dna=son_dna,
                _min_value=self.min_cod_ind_value,
                _max_value=self.max_cod_ind_value
            )
        son.mutation()
        return son
    
    def calculate_population_score(self):
        score = 0
        for i in self.population:
            score += i.score / self.quantity
        self.score = score
        
    def get_best_individual_constants(self):
        self.__order_by_individual_score()
        best_individual = self.population[-1]
        return best_individual.decode_dna_variables_to_decimal()
        
        

class GeneticAlgorithm:
    def __init__(self,
                 _populations_quantity,
                 _population_min, 
                 _population_max, 
                 _individual_dna_length,
                 _individual_encoded_variables_quantity,
                 _individual_muatition_intensity,
                 _min_cod_ind_value,
                 _max_cod_ind_value,
                 _environment
        ):
        self.populations = []
        self.environment = _environment
        self.min_ag_dna_val = _min_cod_ind_value
        self.max_ag_dna_val = _max_cod_ind_value
        self.individual_encoded_variables_quantity = _individual_encoded_variables_quantity
        self.max_function_val = self.max_ag_dna_val * self.individual_encoded_variables_quantity
        for _ in range(_populations_quantity):
            self.populations.append(
                Population(
                    _quantity=random.randint(_population_min, _population_max),
                    _encoded_variables_quantity=_individual_encoded_variables_quantity,
                    _dna_length=_individual_dna_length,
                    _mutation_intensity=_individual_muatition_intensity,
                    _min_cod_ind_value=_min_cod_ind_value,
                    _max_cod_ind_value=_max_cod_ind_value
                )
            )
        
    def evolution(self, _market, _wallet, _initial_amount, _evaluation_intervals, _generations):
        populations_length = len(self.populations) - 1
        while populations_length >= 0:
            population = self.populations[populations_length]
            for gen in range(_generations):
                population_length = self.populations[populations_length].quantity - 1
                while population_length >= 0:
                    individual = population.population[population_length]
                    evaluation = self.__evaluate(individual, _evaluation_intervals)
                    
                    _wallet.restart()
                    _wallet.deposit_coin_1(_initial_amount)
                    stop_loss_list = []
                    for e in evaluation:
                        if e["percent_to_buy"] > 0.05:
                            coin_1_quantity = e['percent_to_buy'] * _wallet.get_balance_in_coin1()
                            coin_2_quantity, coin_2_price = _market.transaction_at_moment(coin_1_quantity, e['position_time'])
                            _wallet.buy_coin_2(coin_1_quantity, coin_2_quantity)
                            stop_loss_list.append(
                                {
                                    'price': coin_2_price - (coin_2_price * 0.05),
                                    'quantity': coin_2_quantity
                                }
                            )
                            count_sl = 0
                            sl_length = len(stop_loss_list)
                            while count_sl < sl_length:
                                stop_loss = stop_loss_list[count_sl]
                                if stop_loss['price'] < coin_2_price:
                                    _, coin_2_sl_price = _market.transaction_at_moment(0, e['position_time'])
                                    coin_1_sl_quantity = stop_loss['quantity'] / coin_2_sl_price
                                    _wallet.sell_coin_2(coin_1_sl_quantity, stop_loss['quantity'])
                                    stop_loss_list.pop(count_sl)
                                    sl_length -= 1
                                count_sl += 1
                                
                        total_earn = _wallet.get_total_balance_in_coin1(_market.get_last_price())
                        individual.set_score(total_earn/_initial_amount)
                        population_length -= 1  
                population.breed()
                population.calculate_population_score()
                print("++++++++++++++++++++++GEN {}++++++++++++++++++++++".format(gen))
                print(population.score, population.get_best_individual_constants())
            populations_length -= 1
            
    def optimized_fit_function(self, _data):
        pass
            
    def __evaluate(self, individual, _evaluation_intervals):
        ag_variables = individual.decode_dna_variables_to_decimal()
        evaluated = []
        lse = len(self.environment)
        to_test_2 = []
        for temp in self.environment:
            to_evaluation = []
            count_var = 0
            for var in temp:
                to_evaluation.append(
                    (var, ag_variables[count_var])
                )
                count_var += 1
            evaluated.append(self.__function(to_evaluation))
            le = len(evaluated)
            if le > _evaluation_intervals and le +_evaluation_intervals <= lse:
                e = evaluated[-_evaluation_intervals:]
                regresion_plus_1_val = self.__linear_regresion_of_evaluated_interval_n_plus_1(e)
                to_test_2.append(
                    {
                        'position_time': le + 1,
                        'regresion_plus_1_val': regresion_plus_1_val,
                        'percent_to_buy': self.__buy(regresion_plus_1_val)
                    }
                )
        return to_test_2
        
        # Toca comprar cuando evaluated tenga algunos valores
        
    def __buy(self, e):
        normalized_evaluated = self.__normalize_evaluated(e)
        return self.__percent_to_buy(normalized_evaluated)
    
    def __linear_regresion_of_evaluated_interval_n_plus_1(self, _evaluated_interval):
        t = [i for i in range(len(_evaluated_interval))]
        reg = linregress(
            x=t,
            y=_evaluated_interval
        )
        return reg[0] * t[-1] + 1 + reg[1]

    def __normalize_evaluated(self, e):
        return e /  self.max_function_val 

    def __percent_to_buy(self, ne):
        return ne if self.__buy_condition(ne) else 0       
        
    def __buy_condition(self, _value):
        return _value > 0
        
    def __function(self, to_eval):
        lambdas = []
        for v in to_eval:
            lambdas.append(
                {
                    
                    'func': lambda x : x[0] * x[1],
                    'eval': v # (variable_data, valor ag)
                }
            )
        return self.__sum_n_functions_recursively(lambdas)
        
    def __sum_n_functions_recursively(self, to_eval):
        if not to_eval:
            return 0
        return to_eval[0]['func'](to_eval[0]['eval']) + self.__sum_n_functions_recursively(to_eval[1:])
        
        