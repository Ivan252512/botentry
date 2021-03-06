import numpy as np
import random

from scipy.stats import linregress

from apps.trades.ia.utils.utils import (
    SimulateBasicWallet,
    SimulateShort
)

from apps.trades.ia.utils.binary_tree import (
    BinaryTree
)

from multiprocessing import Pool

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
        self.encoded_variables_quantity = _encoded_variables_quantity
        self.mutation_intensity = _mutation_intensity 
        self.dna = _dna if _dna else self.generate_individual(
            self.length,
            self.encoded_variables_quantity
        )
        self.score = 0
        self.min_value = _min_value
        self.max_value = _max_value
        self.relevant_info = []
        self.evaluated_function = []

    @staticmethod
    def generate_individual(length, encoded_variables_quantity):
        """Generate n bits strings individual

        :param nbits: String length simulating the bits quantity
        :type nbits: int

        """
        count = 0
        individual = ""
        all_dna_length = length * encoded_variables_quantity
        while(count < all_dna_length):
            individual += str(random.randint(0, 1))
            count += 1
        return individual

    def decode_dna_variables_to_decimal(self):
        dnas = cut_dna(self.dna, self.length)
        decoded_variables = []
        for gen in dnas:
            decoded_variables.append(
                self.binary_to_decimal(gen, self.min_value, self.max_value)
            )
        return decoded_variables

    def mutation(self):
        bin = list(self.dna)
        for _ in range(random.randint(0, self.mutation_intensity)):
            rand = random.randint(0, self.length - 1)
            if(bin[rand] == "0"):
                bin[rand] = "1"
            if(bin[rand] == "1"):
                bin[rand] = "0"
        self.dna = "".join(bin)

    def set_score(self, _score):
        self.score = _score

    def add_relevant_info(self, _info):
        self.relevant_info.append(_info)
        

    @staticmethod
    def binary_to_decimal(gen, a, b):
        """ Converts binary values into a decimal values with one comma, between 
        [a,b] interval

        :param bin: String binary value
        :type bin: String:
        :param a: Start interval
        :type a: int
        :param b: End interval
        :type b: int
        """
        n_count = len(gen)
        n = n_count
        dec = 0
        for i in gen:
            if i == '1':
                dec += 2**(n_count-1)
            n_count -= 1
        return a+((dec)/(2**n-1))*(b-a)
    
    def __str__(self):
        return self.dna


def cut_dna(dna, len_interval):
    if len(dna) % len_interval:
        raise Exception("The length of dna must be multiple of len_interval ")
    if len(dna) == len_interval:
        return [dna]
    return [dna[:len_interval]] + cut_dna(dna[len_interval:], len_interval)


class Population:

    def __init__(self,
                 _quantity,
                 _encoded_variables_quantity,
                 _dna_length,
                 _mutation_intensity,
                 _min_cod_ind_value,
                 _max_cod_ind_value,
                 _population_origin=None
                 ):
        self.quantity = _quantity
        self.dna_length = _dna_length
        self.encoded_variables_quantity = _encoded_variables_quantity
        self.mutation_intensity = _mutation_intensity
        self.min_cod_ind_value = _min_cod_ind_value
        self.max_cod_ind_value = _max_cod_ind_value
        self.score = 0
        self.population = self.generate_population(
            _population_origin=_population_origin)

    def generate_population(self, _population_origin):
        if not _population_origin:
            population = []
            count = 0
            while(count < self.quantity):
                individual = Individual(
                    _length=self.dna_length,
                    _encoded_variables_quantity=self.encoded_variables_quantity,
                    _mutation_intensity=self.mutation_intensity,
                    _min_value=self.min_cod_ind_value,
                    _max_value=self.max_cod_ind_value
                )
                population.append(individual)
                count += 1
            return population
        else:
            population = []
            count = 0
            while(count < self.quantity):
                length_pop_orig = len(_population_origin)
                idx = random.randint(0, length_pop_orig - 1)
                new_or_old = random.randint(0, 10)
                if new_or_old == 0:
                    population.append(_population_origin[idx])
                else:
                    individual = Individual(
                        _length=self.dna_length,
                        _encoded_variables_quantity=self.encoded_variables_quantity,
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
        best_half = self.population[half:]
        ten_percent = int(self.quantity/10)
        best_ten_percent = self.population[ten_percent:]

        new_population = []
        for _ in range(half * 2):
            mother = best_ten_percent[random.randint(0, ten_percent - 1)]
            father = best_half[random.randint(0, half - 1)]
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

        self.population = current_generation

    def __order_by_individual_score(self):
        self.population.sort(key=lambda individual: individual.score)

    def __cross_genes(self, father, mother):
        son_dna = ""
        for i in range(father.length * father.encoded_variables_quantity):
            rand = random.randint(0, 1)
            if (rand == 0):
                son_dna += father.dna[i]
            else:
                son_dna += mother.dna[i]
        son = Individual(
            _length=father.length,
            _encoded_variables_quantity=father.encoded_variables_quantity,
            _mutation_intensity=father.mutation_intensity,
            _dna=son_dna,
            _min_value=father.min_value,
            _max_value=father.max_value
        )
        son.mutation()
        return son

    def calculate_population_score(self):
        self.__order_by_individual_score()
        return self.population[-1].score

    def get_best_individual(self):
        self.__order_by_individual_score()
        best_individual = self.population[-1]
        return best_individual

    def get_best_individual_constants(self):
        self.__order_by_individual_score()
        best_individual = self.population[-1]
        return best_individual.decode_dna_variables_to_decimal()
    
    def get_best_individual_evaluated_function(self):
        self.__order_by_individual_score()
        best_individual = self.population[-1]
        return best_individual.evaluated_function

    def get_best_individual_score(self):
        self.__order_by_individual_score()
        best_individual = self.population[-1]
        return best_individual.score

    def get_best_individual_operations(self):
        self.__order_by_individual_score()
        best_individual = self.population[-1]
        return best_individual.relevant_info

    def get_best_twenty_percent_individuals(self):
        self.__order_by_individual_score()
        twenty_percent = int(self.quantity / 5)
        return self.population[:twenty_percent]

    def get_greatest_individual(self):
        self.__order_by_individual_score()
        constants = self.get_best_individual_constants()
        score = self.get_best_individual_score()
        operations = self.get_best_individual_operations()
        return score, constants, operations


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
                 _environment,
                 _stop_loss_percent,
                 _stop_loss_divisor_plus,
                 _keys,
                 _variables,
                 _individual_relevant_info=False,
                 ):
        self.populations = []
        self.populations_quantity = _populations_quantity
        self.population_min = _population_min
        self.population_max = _population_max
        self.individual_dna_length = _individual_dna_length
        self.individual_encoded_variables_quantity = _individual_encoded_variables_quantity
        self.individual_muatition_intensity = _individual_muatition_intensity
        self.environment = _environment
        self.periods_environment = len(_environment)
        self.min_ag_dna_val = _min_cod_ind_value
        self.max_ag_dna_val = _max_cod_ind_value
        self.max_function_val = self.max_ag_dna_val * \
            self.individual_encoded_variables_quantity
        self.individual_relevant_info = _individual_relevant_info
        self.evaluated = BinaryTree(0, 0)
        self.stop_loss_percent = _stop_loss_percent
        self.stop_loss_divisor_plus = _stop_loss_divisor_plus
        self.keys = _keys
        self.variables = _variables
        self.type_variables_to_evaluate_ag = ["cross"]
        for _ in range(self.populations_quantity):
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

    def evolution(self, _market, _initial_amount, _evaluation_intervals, _generations_pob, _generations_ind):
        populations = self.populations
        for gen in range(_generations_pob):
            t = Pool(processes=1)
            data = []
            for population in self.populations:
                data.append(
                    {
                        'market': _market,
                        'initial_amount': _initial_amount,
                        'evaluation_intervals': _evaluation_intervals,
                        'generations': _generations_ind,
                        'population': population
                    }
                )
            self.individual_relevant_info = gen == _generations_pob - 1
            populations = t.map(self.optimized_population_function, data)
            t.close()

            print(
                "++++++++++++++Poblaciones gen: {}/{}+++++++++++++++++".format(gen, _generations_pob))
            self.populations = populations
            print(self.get_greatest_individual())

            if gen < _generations_pob - 1:
                self._new_populations(_old_populations=populations)

        return self.get_greatest_individual()

    def evolution_individual_optimized(self, _market, _initial_amount, _evaluation_intervals, _generations_pob, _generations_ind):
        populations = self.populations
        for gen in range(_generations_pob):
            data = []
            for population in self.populations:
                data.append(
                    {
                        'market': _market,
                        'initial_amount': _initial_amount,
                        'evaluation_intervals': _evaluation_intervals,
                        'generations': _generations_ind,
                        'population': population
                    }
                )
            self.individual_relevant_info = gen == _generations_pob - 1
            populations = list(map(self.optimized_population_and_individual_function, data))

            # print(
            #     "++++++++++++++Poblaciones gen: {}/{}+++++++++++++++++".format(gen, _generations_pob))
            self.populations = populations
            # print(self.get_greatest_individual())

            if gen < _generations_pob - 1:
                self._new_populations(_old_populations=populations)

        return self.get_greatest_individual()

    def get_greatest_individual(self):
        self.__order_by_population_score()
        best = self.populations[-1]
        constants = best.get_best_individual_constants()
        score = best.get_best_individual_score()
        operations = best.get_best_individual_operations()
        best_individual = best.get_best_individual()
        evaluated_function = best.get_best_individual_evaluated_function()
        return score, constants, operations, best_individual, evaluated_function

    def __order_by_population_score(self):
        self.populations.sort(key=lambda population: population.score)

    def _new_populations(self, _old_populations):
        self.__order_by_population_score()
        self.populations = self.populations[:int(
            0.1 * self.populations_quantity)]
        for _ in range(int(self.populations_quantity * 0.9)):
            self.populations.append(
                Population(
                    _quantity=random.randint(
                        self.population_min, self.population_max),
                    _encoded_variables_quantity=self.individual_encoded_variables_quantity,
                    _dna_length=self.individual_dna_length,
                    _mutation_intensity=self.individual_muatition_intensity,
                    _min_cod_ind_value=self.min_ag_dna_val,
                    _max_cod_ind_value=self.max_ag_dna_val
                )
            )

    def optimized_population_function(self, _data):
        market = _data['market']
        initial_amount = _data['initial_amount']
        evaluation_intervals = _data['evaluation_intervals']
        generations = _data['generations']
        population = _data['population']
        sl_percent = self.stop_loss_percent
        sl_divisor_plus = self.stop_loss_divisor_plus

        for gen in range(generations):
            population_length = population.quantity - 1
            while population_length >= 0:
                individual = population.population[population_length]
                _wallet = SimulateBasicWallet()
                _wallet.deposit_coin_1(initial_amount)
                if True: #individual.score == 0:
                    evaluation, evaluated = self.__evaluate(
                        individual, evaluation_intervals)
                    individual.evaluated_function = evaluated
                    for e in evaluation:
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
                        if len(individual.relevant_info) > 0 and "coin_1_sell_quantity" in individual.relevant_info[-1]:
                            _, coin_2_last_price_price = market.transaction_at_moment_sell_coin2(
                                0, e['position_time'])
                            sl = individual.relevant_info[-1]["stop_loss"][-1]
                            if coin_2_last_price_price < sl:
                                coin_2_quantity = _wallet.get_balance_in_coin2()
                                if coin_2_quantity > 0:
                                    coin_1_quantity_market, coin_2_price_market = market.transaction_at_moment_sell_coin2(
                                        coin_2_quantity, e['position_time'])
                                    coin_2_price_sl = individual.relevant_info[-1]["stop_loss"][-1]
                                    coin_1_quantity_sl = coin_2_price_sl * coin_2_quantity
                                    coin_2_price = coin_2_price_sl if coin_2_price_sl < coin_2_price_market else coin_2_price_market
                                    coin_1_quantity = coin_1_quantity_sl if coin_2_price_sl < coin_2_price_market else coin_1_quantity_market
                                    # self.individual_relevant_info:
                                    if _wallet.sell_coin_2(coin_1_quantity, coin_2_quantity):
                                        individual.add_relevant_info({
                                            'coin_1_buy_quantity': coin_1_quantity,
                                            'coin_2_sell_quantity': sl,
                                            'coin_2_sell_price': coin_2_price,
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
                    individual.set_score(score)
                population_length -= 1
            score = population.calculate_population_score()
            print(f"Gen {gen} score: {score} ")
            population.breed()
        return population

    def optimized_population_and_individual_function(self, _data):
        market = _data['market']
        initial_amount = _data['initial_amount']
        evaluation_intervals = _data['evaluation_intervals']
        generations = _data['generations']
        population = _data['population']

        for gen in range(generations):
            t = Pool(processes=12)
            data = []
            for individual in population.population:
                exists_tree, val_tree = self.evaluated.search(individual.dna)
                if exists_tree is not False and val_tree is not None:
                    individual.score = val_tree
                data.append(
                    {
                        'market': market,
                        'initial_amount': initial_amount,
                        'evaluation_intervals': evaluation_intervals,
                        'individual': individual
                    }
                )
            individuals = t.map(self.optimized_individual_function, data)
            t.close()
            for individual in individuals:
                self.evaluated.insert(individual.dna, individual.score)
            population.population = individuals
            score = population.calculate_population_score()
            if gen % 1 == 0:
                print(f"Gen {gen} score: {score} ")
            population.breed()
        return population

    def optimized_individual_function(self, _data):
        
        individual = _data['individual']     
        
        if individual.score != 0 and individual.relevant_info:
            return individual
          
        market = _data['market']
        initial_amount = _data['initial_amount']
        evaluation_intervals = _data['evaluation_intervals']
        sl_percent = self.stop_loss_percent
        sl_divisor_plus = self.stop_loss_divisor_plus

        _wallet = SimulateBasicWallet()
        _short = SimulateShort()
        _wallet.deposit_coin_1(initial_amount)
        if individual.score == 0 or not individual.relevant_info:
            evaluation, evaluated = self.__evaluate(individual, evaluation_intervals)
            individual.evaluated_function = evaluated
            for e in evaluation:
                if e["position_time"] < self.periods_environment:
                    if e["buy"]:
                        # print(e)
                        
                        coin_1_quantity = _wallet.get_balance_in_coin1()
                        if coin_1_quantity > 10:
                            coin_2_quantity, coin_2_price = market.transaction_at_moment_buy_coin2(
                                coin_1_quantity, e['position_time'])
                            # Short
                            profit = _short.close(coin_2_price)
                            _wallet.deposit_coin_1(profit)
                            coin_1_quantity = _wallet.get_balance_in_coin1()
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
                                # Short
                                _short.short(coin_2_price_market, coin_2_quantity)
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
            individual.set_score(score)
        return individual

    def __evaluate_last(self, individual, _evaluation_intervals):
        ag_variables = individual.decode_dna_variables_to_decimal()
        evaluated = []
        to_test_2 = []
        for temp in self.environment:
            to_evaluation = []
            count_var = 0
            for var in temp:
                to_evaluation.append(
                    (var, ag_variables[count_var])
                )
                count_var += 1
            evaluated.append(self.__simplified_function(to_evaluation))
            le = len(evaluated)
            if le > _evaluation_intervals: #TODO MAGIA
                e = evaluated[-_evaluation_intervals:]
                regresion_plus_1_val = self.__linear_regresion_of_evaluated_interval_n_plus_1(
                    e)
                to_test_2.append(
                    {
                        'position_time': le + _evaluation_intervals + 1,
                        'regresion_plus_1_val': regresion_plus_1_val,
                        'buy': self.__buy_condition(regresion_plus_1_val),
                        'sell': self.__sell_condition(regresion_plus_1_val),
                    }
                )
            
        return to_test_2, evaluated
    
    
    def __evaluate(self, individual, _evaluation_intervals):
        ag_variables = individual.decode_dna_variables_to_decimal()
        to_test_2 = []
        position = 0 
        interval = _evaluation_intervals
        while position + interval  <= len(self.environment):
            var = {}
            for k in range(len(self.keys)):
                var[self.keys[k]] = []
                for se in self.environment[position:position+interval]:
                    var[self.keys[k]] += [se[k]]
            polinomial_strategy = self.polinomial_strategy(var, ag_variables)
            to_test_2.append(
                {
                    'position_time': position + interval,
                    'buy': polinomial_strategy[0],
                    'sell': polinomial_strategy[1],
                }
            )
            position += 1
                
        return to_test_2, []
    
    def MACD_strategy(self, value, ag_variables):
        low = np.array(value.get('low')) 
        
        # print(value)
        
        macd = np.array(value.get('macd', low)) * ag_variables[0] + ag_variables[1] 
        signal = np.array(value.get('signal', low)) * ag_variables[2] + ag_variables[3] 
        histogram = np.array(value.get('histogram', low)) * ag_variables[4] + ag_variables[5] 
        ema_5 = np.array(value.get('ema_5', low)) * ag_variables[6] + ag_variables[7] 
        ema_10 = np.array(value.get('ema_10', low)) * ag_variables[8] + ag_variables[9] 
        ema_20 = np.array(value.get('ema_20', low)) * ag_variables[10] + ag_variables[11] 
        
        cross_macd = self.cross_variable(macd, signal)
        cross_ema_5_10 = self.cross_variable(ema_5, ema_20)
        cross_ema_10_20 = self.cross_variable(ema_10, ema_20)
        slope_histogram = self.slope(histogram)
        slope_ema_5 = self.slope(ema_5)
        slope_ema_10 = self.slope(ema_10)
        slope_ema_20 = self.slope(ema_20)
        
        buy_macd = False
        sell_macd = False
        if slope_ema_5[0] and slope_ema_10[0] and slope_ema_20[0]:
            buy_macd = True
        if slope_ema_5[1] and slope_ema_10[1] and slope_ema_20[1]:
            sell_macd = True
            
        return buy_macd, sell_macd            
    
    def polinomial_strategy(self, value, ag_variables):
        
        k = list(value.keys())
        
        
        y = [0 for _ in value[k[0]]]
        for i in range(len(value)):
            to_evaluate = False
            for j in self.type_variables_to_evaluate_ag:
                if j in k[i]:
                    to_evaluate =  True
                    break
            if to_evaluate:
                y += np.array(value[k[i]]) * ag_variables[i]
            
        if len(y) % 2 != 0:
            raise ValueError("Intarval must be a pair number")
            
        # print(y)    
        return np.mean(y) > 0.25, np.mean(y) < - 0.25
        
        #l_m =int(len(y) / 4)
        #

        #s0 = self.slope(y[:3 * l_m])
        #s1 = self.slope(y[3 * l_m:])
        #
        #return s0[-1] < s1[-1], s0[-1] > s1[-1]
        
        

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
        return [i * reg[0] + reg[1] for i in t]
    

        # Toca comprar cuando evaluated tenga algunos valores

    def __buy(self, e):
        normalized_evaluated = self.__normalize_evaluated(e)
        return self.__percent_to_buy(normalized_evaluated)

    def __linear_regresion_of_evaluated_interval_n_plus_1(self, _evaluated_interval):
        t = [i for i in range(len(_evaluated_interval))]
        # middle_index = int(len(_evaluated_interval) / 2)
        reg_1 = linregress(
            x=t[:-4],
            y=_evaluated_interval[:-4]
        )
        reg_2 = linregress(
            x=t[-4:],
            y=_evaluated_interval[-4:]
        )
        return reg_1[0], reg_2[0]
        

    def __normalize_evaluated(self, e):
        return e / self.max_function_val

    def __percent_to_buy(self, ne):
        return ne if self.__buy_condition(ne) else 0

    def __buy_condition(self, _value):
        # print("VALOR: " , _value, _value[0] > 0.1 and _value[1] < 0.1 and _value[1] < 0)
        return  _value[0] < 0 and _value[1] >= 0 
    
    def __sell_condition(self, _value):
        # print("VALOR: " , _value, _value[0] > 0.1 and _value[1] < 0.1 and _value[1] < 0)
        return  _value[0] >= 0 and _value[1] < 0 

    def __simplified_function(self, to_eval):
        eval = []
        for v in to_eval:
            eval.append(
                v[0] * v[1]
            )
        return sum(eval)

    def __function(self, to_eval):
        lambdas = []
        for v in to_eval:
            lambdas.append(
                {

                    'func': lambda x: x[0] ** x[1],
                    'eval': v  # (variable_data, valor ag)
                }
            )
        return self.__sum_n_functions_recursively(lambdas)

    def __sum_n_functions_recursively(self, to_eval):
        if not to_eval:
            return 0
        return to_eval[0]['func'](to_eval[0]['eval']) + self.__sum_n_functions_recursively(to_eval[1:])
