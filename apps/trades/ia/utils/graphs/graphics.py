import matplotlib.pyplot as plt
import mplfinance as fplt
import pandas as pd
import matplotlib.dates as mpdates
import datetime
import boto3

import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.stats import linregress

import datetime
from pathlib import Path

from apps.trades.binance.client import Client

import traceback
import time

from django.conf import settings

# https://www.geeksforgeeks.org/plot-candlestick-chart-using-mplfinance-module-in-python/
# https://coderzcolumn.com/tutorials/data-science/candlestick-chart-in-python-mplfinance-plotly-bokeh

class Graphic:

    def __init__(self, _raw_data, _pair, _trading_interval):
        self.raw_data = _raw_data
        self.length = len(_raw_data)
        self.trading_interval = _trading_interval
        self.pair = _pair
        self.processed_data = None
        self.ma = None 
        self.graphic = None 
        self.indicators = []
        self.maxs_columns = []
        self.mins_columns = []
        self.exclude_to_ag = ["open", "low", "high", "close", "volume"]
        self.graph_ag = []
        self.not_to_graph_indicators = []
        self.fibos = [0, 0.236, 0.382, 0.500, 0.618, 0.786, 1, 1.618]
        
    def process_data(self):
        
        all_data = []
        
        for data in self.raw_data:
            all_data.append(
                [
                    datetime.datetime.fromtimestamp(data[0] / 1000),
                    float(data[1]),
                    float(data[2]),
                    float(data[3]),
                    float(data[4]),
                    float(data[5]),     
                ]
            )
        
        df = pd.DataFrame(
            all_data,
            columns=[
                "date",
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]
        )
        
        datetime_series = pd.to_datetime(df['date'])
        datetime_index = pd.DatetimeIndex(datetime_series.values)
        
        df2 = df.set_index(datetime_index)
        df2.drop('date', axis=1, inplace=True)
        
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        #     print(df2)
        
        self.processed_data = df2
        
    def calculate_moving_average(self, _periods):
        self.processed_data['ma_{}'.format(_periods)] = self.processed_data.ewm(span=_periods, adjust=False).mean()
        self.indicators.append('ma_{}'.format(_periods))
        # self.exclude_to_ag.append('ma_{}'.format(_periods))
        self.graph_ag.append('ma_{}'.format(_periods))
        
        
    def calculate_exponential_moving_average(self, _periods, _graphic=True):
        self.processed_data['ema_{}'.format(_periods)] = self.processed_data.iloc[:,0].ewm(span=_periods,adjust=False).mean()
        if _graphic:
            self.indicators.append('ema_{}'.format(_periods))
            self.graph_ag.append('ema_{}'.format(_periods))
            
    def calculate_macd(self):
        self.processed_data['macd'] = self.processed_data['ema_12'] - self.processed_data['ema_26']
        self.indicators.append('macd')
        # self.exclude_to_ag.append('ma_{}'.format(_periods))
        self.graph_ag.append('macd')
        
    def calculate_signal(self):
        self.processed_data['signal'] = self.processed_data['macd'].ewm(span=9, adjust=False).mean()
        self.indicators.append('signal')
        # self.exclude_to_ag.append('ma_{}'.format(_periods))
        self.graph_ag.append('signal')
        
    def calculate_histogram(self):
        self.processed_data['histogram'] = self.processed_data['macd'] - self.processed_data['signal']
        self.indicators.append('histogram')
        # self.exclude_to_ag.append('ma_{}'.format(_periods))
        self.graph_ag.append('histogram')
        
    def calculate_fibonacci_retracement(self):
        count = 1
        for fb in self.fibos:
            max = self.processed_data['high'].max()
            min = self.processed_data['low'].min() 
            self.processed_data['fr_{}'.format(count)] = [min + fb * (max - min) for _ in self.raw_data]
            self.indicators.append('fr_{}'.format(count))
            self.graph_ag.append('fr_{}'.format(count))
            self.exclude_to_ag.append('fr_{}'.format(count))
            count += 1
            
    def calculate_bollinger_bands(self):
        pass
    
    def calculate_stochastic_oscillator(self):
        pass
    
    def get_second_derivative(self, _sigma_gaussian_filter):
        # Secdond derivative
        filtered_data_low = gaussian_filter1d(self.processed_data['low'], _sigma_gaussian_filter)
        filtered_data_high = gaussian_filter1d(self.processed_data['high'], _sigma_gaussian_filter)
        self.processed_data['fd_low_{}'.format(_sigma_gaussian_filter)] = filtered_data_low
        # self.not_to_graph_indicators.append('fd_low_{}'.format(_sigma_gaussian_filter))
        self.indicators.append('fd_low_{}'.format(_sigma_gaussian_filter))
        self.exclude_to_ag.append('fd_low_{}'.format(_sigma_gaussian_filter))
        self.processed_data['d2_low_{}'.format(_sigma_gaussian_filter)] = np.gradient(np.gradient(filtered_data_low))
        # self.not_to_graph_indicators.append('d2_low_{}'.format(_sigma_gaussian_filter))
        self.indicators.append('d2_low_{}'.format(_sigma_gaussian_filter))
        self.exclude_to_ag.append('d2_low_{}'.format(_sigma_gaussian_filter))
        self.processed_data['fd_high_{}'.format(_sigma_gaussian_filter)] = filtered_data_high
        # self.not_to_graph_indicators.append('fd_high_{}'.format(_sigma_gaussian_filter))
        self.indicators.append('fd_high_{}'.format(_sigma_gaussian_filter))
        self.exclude_to_ag.append('fd_high_{}'.format(_sigma_gaussian_filter))
        self.processed_data['d2_high_{}'.format(_sigma_gaussian_filter)] = np.gradient(np.gradient(filtered_data_high))
        # self.not_to_graph_indicators.append('d2_high_{}'.format(_sigma_gaussian_filter))
        self.indicators.append('d2_high_{}'.format(_sigma_gaussian_filter))
        self.exclude_to_ag.append('d2_high_{}'.format(_sigma_gaussian_filter))
        self._put_min_respectly_in_data_df('low', 'd2_low_{}'.format(_sigma_gaussian_filter), _sigma_gaussian_filter)
        self._put_max_respectly_in_data_df('high', 'd2_high_{}'.format(_sigma_gaussian_filter),_sigma_gaussian_filter)
        for i in self.indicators:
            if "d2" in i:
                self.exclude_to_ag.append(i)
        
    def _put_min_respectly_in_data_df(self, _df, _df2, _sigma_gaussian_filter):
        df = self.processed_data
        self.processed_data['min'] = df[_df][(df[_df2].shift(1) < df[_df2]) & (df[_df2].shift(-1) < df[_df2])]
        self.indicators.append('min')
        self.exclude_to_ag.append('min')
        
        # dates_intervals = np.array([i for i in range(self.length)])
        # mask = ~np.isnan(dates_intervals[400:]) & ~np.isnan(self.processed_data['min_correspondent_{}_{}'.format(_df ,_df2)][400:])        
        # reg = linregress(
        #     x=dates_intervals[400:][mask],
        #     y=self.processed_data['min_correspondent_{}_{}'.format(_df ,_df2)][400:][mask]
        # )
        # self.processed_data['reg_mn_correspondent_{}_{}'.format(_df ,_df2)] = reg[0] * dates_intervals + reg[1]
        # self.indicators.append('reg_mn_correspondent_{}_{}'.format(_df ,_df2))
    
    def _put_max_respectly_in_data_df(self, _df, _df2, _sigma_gaussian_filter):
        df = self.processed_data
        self.processed_data['max'] = df[_df][(df[_df2].shift(1) > df[_df2]) & (df[_df2].shift(-1) > df[_df2])]
        self.indicators.append('max')
        self.exclude_to_ag.append('max')

        # dates_intervals = np.array([i for i in range(self.length)])
        # mask = ~np.isnan(dates_intervals[400:]) & ~np.isnan(self.processed_data['max_correspondent_{}_{}'.format(_df ,_df2)][400:])        
        # reg = linregress(
        #     x=dates_intervals[400:][mask],
        #     y=self.processed_data['max_correspondent_{}_{}'.format(_df ,_df2)][400:][mask]
        # )
        # self.processed_data['reg_mx_correspondent_{}_{}'.format(_df ,_df2)] = reg[0] * dates_intervals + reg[1]
        # self.indicators.append('reg_mx_correspondent_{}_{}'.format(_df ,_df2))
        
    def get_processed_data(self):
        return self.processed_data.copy()
    
    def get_normalized_processed_data(self):
        df = self.processed_data.copy()
        result = self.processed_data.copy()
        for feature_name in df.columns:
            max_value = df[feature_name].max()
            min_value = df[feature_name].min()
            result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
        # result = result.drop(columns=self.exclude_to_ag, axis=1)
        result = result.replace(np.nan, 0)
        return result
    
    
    def get_indicators(self):
        return self.indicators.copy()
        
    def graph(self):
        subplots = []
        # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        #     print(self.processed_data)
        count_max = 1
        count_min = 1
        for i in self.indicators:
            if i not in self.not_to_graph_indicators:
                if "max" in i:
                    subplots.append(
                        fplt.make_addplot(
                            self.processed_data[i],
                            type='scatter',
                            markersize=15,
                            marker='v'
                        )
                    )
                    count_max += 1
                elif "min" in i:
                    subplots.append(
                        fplt.make_addplot(
                            self.processed_data[i],
                            type='scatter',
                            markersize=15,
                            marker='^'
                        )
                    )
                    count_min += 1
                else:
                    # if "d2" in i:
                    #     subplots.append(
                    #         fplt.make_addplot(
                    #             self.processed_data[i],
                    #             type='scatter',
                    #             markersize=0.1,
                    #             marker='+'
                    #         )
                    #     )
                    if "ma" in i:
                        subplots.append(
                            fplt.make_addplot(
                                self.processed_data[i],
                                type='scatter',
                                markersize=0.1,
                                marker='.'
                            )
                        )
                    elif "fr" in i:
                        subplots.append(
                            fplt.make_addplot(
                                self.processed_data[i],
                                type='scatter',
                                markersize=0.1,
                                marker='*'
                            )
                        )
                
        Path(
            "graphics/{}/{}/pd/".format(
                self.pair,
                self.trading_interval
            )
        ).mkdir(parents=True, exist_ok=True)
        current_date = datetime.datetime.now()
        save= dict(
            fname="graphics/{}/{}/pd/{}.png".format(
                self.pair,
                self.trading_interval,
                current_date.strftime("%m_%d_%Y_%H_%M_%S")
            ),
            dpi=300,
        )

        fplt.plot(
            self.processed_data,
            type='candle',
            style='charles',
            title=self.pair,
            ylabel='Price ($)',
            volume=True,
            ylabel_lower='Shares\nTraded',
            addplot=subplots,
            savefig=save
        ) 
        
    def graph_for_ag(self, _initial, _score, _last_operation):
        subplots = []
        print(self.graph_ag)
        for i in self.graph_ag:
            if "sells" in i:
                subplots.append(
                    fplt.make_addplot(
                        self.processed_data[i],
                        type='scatter',
                        markersize=10,
                        marker='v',
                        color="green"
                        
                    )
                )
            elif "buys" in i:
                subplots.append(
                    fplt.make_addplot(
                        self.processed_data[i],
                        type='scatter',
                        markersize=10,
                        marker='^',
                        color="red"
                    )
                )
            elif "stop_loss" in i:
                subplots.append(
                    fplt.make_addplot(
                        self.processed_data[i],
                        type='scatter',
                        markersize=2,
                        marker='*',
                        color="blue"
                    )
                )
            else:
                if "d2" in i:
                    subplots.append(
                        fplt.make_addplot(
                            self.processed_data[i],
                            type='scatter',
                            markersize=0.1,
                            marker='+'
                        )
                    )
                elif "ma" in i:
                    subplots.append(
                        fplt.make_addplot(
                            self.processed_data[i],
                            type='scatter',
                            markersize=0.1,
                            marker='o'
                        )
                    )
                elif "fr" in i:
                    subplots.append(
                        fplt.make_addplot(
                            self.processed_data[i],
                            type='scatter',
                            markersize=0.1,
                            marker='*'
                        )
                    )
                elif "evaluated_function" in i:
                    subplots.append(
                        fplt.make_addplot(
                            self.processed_data[i],
                            type='line'
                        )
                    )

        current_date = datetime.datetime.now()
        name_file = current_date.strftime("%m_%d_%Y_%H_%M_%S") + ".png"
        ubication_file = "graphics/{}/{}/ag/{}".format(
                self.pair,
                self.trading_interval,
                name_file
            )
        Path(
            "graphics/{}/{}/ag/".format(
                self.pair,
                self.trading_interval
            )
        ).mkdir(parents=True, exist_ok=True)
        save= dict(
            fname=ubication_file,
            dpi=600,
        )

        lo = ""
        for k in _last_operation.keys():
            if not "balance" in k:
                if not "stop_loss" in k:
                    lo += f"{k}: {_last_operation[k]} "
                    
        lo += f"initial: {_initial}, score: {_score} "
        
        s = fplt.make_mpf_style(base_mpf_style='charles', rc={'font.size':2})
        
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
            print(self.processed_data)

        fplt.plot(
            self.processed_data,
            type='candle',
            style=s,
            title=lo,
            ylabel='Price ($)',
            volume=True,
            ylabel_lower='Shares\nTraded',
            addplot=subplots,
            savefig=save
        ) 
        

        # session = boto3.Session(
        #     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        #     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        # )
        # 
        # client = session.client(
        #     's3',
        #     'us-west-2'
        # )

        # client.upload_file(ubication_file, settings.AWS_BUCKET, ubication_file)
        
    def graph_for_evaluated_not_ai(self, _initial, _score, _last_operation):
        subplots = []
        print(self.graph_ag)
        for i in self.graph_ag:
            if "sells" in i:
                subplots.append(
                    fplt.make_addplot(
                        self.processed_data[i],
                        type='scatter',
                        markersize=10,
                        marker='v',
                        color="green"
                        
                    )
                )
            elif "buys" in i:
                subplots.append(
                    fplt.make_addplot(
                        self.processed_data[i],
                        type='scatter',
                        markersize=10,
                        marker='^',
                        color="red"
                    )
                )
            #elif "stop_loss" in i:
            #    subplots.append(
            #        fplt.make_addplot(
            #            self.processed_data[i],
            #            type='scatter',
            #            markersize=2,
            #            marker='*',
            #            color="blue"
            #        )
            #    )
            else:
                if "d2" in i:
                    subplots.append(
                        fplt.make_addplot(
                            self.processed_data[i],
                            type='scatter',
                            markersize=0.1,
                            marker='+'
                        )
                    )
                elif "ema" in i:
                    subplots.append(
                        fplt.make_addplot(
                            self.processed_data[i],
                            type='line',
                        )
                    )
                elif "macd" in i:
                    subplots.append(
                        fplt.make_addplot(
                            self.processed_data[i],
                            type='line',
                            color='green',
                            panel='lower'
                        )
                    )
                elif "signal" in i:
                    subplots.append(
                        fplt.make_addplot(
                            self.processed_data[i],
                            type='line',
                            color='red',
                            panel='lower'
                        )
                    )
                elif "histogram" in i:
                    subplots.append(
                        fplt.make_addplot(
                            self.processed_data[i],
                            type='line',
                            color='black',
                            panel='lower'
                        )
                    )
                # elif "fr" in i:
                #    subplots.append(
                #        fplt.make_addplot(
                #            self.processed_data[i],
                #            type='scatter',
                #            markersize=0.1,
                #            marker='*'
                #        )
                #    )


        current_date = datetime.datetime.now()
        name_file = current_date.strftime("%m_%d_%Y_%H_%M_%S") + ".png"
        ubication_file = "graphics/{}/{}/not_ai/{}".format(
                self.pair,
                self.trading_interval,
                name_file
            )
        Path(
            "graphics/{}/{}/not_ai/".format(
                self.pair,
                self.trading_interval
            )
        ).mkdir(parents=True, exist_ok=True)
        save= dict(
            fname=ubication_file,
            dpi=1400,
        )

        lo = ""
        for k in _last_operation.keys():
            if not "balance" in k:
                if not "stop_loss" in k:
                    lo += f"{k}: {_last_operation[k]} "
                    
        lo += f"initial: {_initial}, score: {_score} "
        
        s = fplt.make_mpf_style(base_mpf_style='charles', rc={'font.size':2})
        
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
            print(self.processed_data)

        fplt.plot(
            self.processed_data,
            type='candle',
            style=s,
            title=lo,
            ylabel='Price ($)',
            ylabel_lower='Shares\nTraded',
            addplot=subplots,
            savefig=save
        ) 
        

                
    def process_data_received_ag(self, data, evaluated_function):
        buys = [np.nan for _ in range(self.length)]
        sells = [np.nan for _ in range(self.length)]
        count_sl = 0
        for d in data:
            if d['position_time'] < self.length:
                if 'coin_1_sell_quantity' in d:
                    buys[d['position_time']] = d['coin_2_buy_price']
                    stop_loss = [None for _ in range(self.length)]
                    count = 0
                    for sl in d['stop_loss']:
                        if d['position_time'] + count < self.length:
                            stop_loss[d['position_time'] + count] = sl
                        count += 1
                    self.processed_data['stop_loss_{}'.format(count_sl)] = stop_loss
                    self.graph_ag.append('stop_loss_{}'.format(count_sl))
                    count_sl += 1
                elif 'coin_1_buy_quantity' in d:
                    sells[d['position_time']] = d['coin_2_sell_price']
        
        if not self.all_nan(buys):        
            self.processed_data['buys'] = buys
            self.graph_ag.extend(["buys"])
        if not self.all_nan(sells):     
            self.processed_data['sells'] = sells
            self.graph_ag.extend(["sells"])
        self.processed_data['evaluated_function'] = evaluated_function
        self.graph_ag.extend(["evaluated_function"])
        # self.graph_ag.extend(["sells", "buys"]) #, "evaluated_function"])
        
        # operacion = "comprar" if 'coin_1_sell_quantity' in data[-1] else "stop_loss_increment"
        return data[-1]
    
    def process_data_received_not_ai(self, data):
        buys = [np.nan for _ in range(self.length)]
        sells = [np.nan for _ in range(self.length)]
        count_sl = 0
        for d in data:
            if d['position_time'] < self.length:
                if 'coin_1_sell_quantity' in d:
                    buys[d['position_time']] = d['coin_2_buy_price']
                    stop_loss = [None for _ in range(self.length)]
                    count = 0
                    for sl in d['stop_loss']:
                        if d['position_time'] + count < self.length:
                            stop_loss[d['position_time'] + count] = sl
                        count += 1
                    self.processed_data['stop_loss_{}'.format(count_sl)] = stop_loss
                    self.graph_ag.append('stop_loss_{}'.format(count_sl))
                    count_sl += 1
                elif 'coin_1_buy_quantity' in d:
                    sells[d['position_time']] = d['coin_2_sell_price']
        
        if not self.all_nan(buys):        
            self.processed_data['buys'] = buys
            self.graph_ag.extend(["buys"])
        if not self.all_nan(sells):     
            self.processed_data['sells'] = sells
            self.graph_ag.extend(["sells"])
            
        return data[-1] if data else {}
    
    
    def all_nan(self, arr):
        arr = pd.DataFrame(arr)
        return arr.isnull().values.all(axis=0)
    
    def get_last_ma_period(self, _period):
        return self.processed_data.get(['ma_{}'.format(_period)][-1], None)
    
    def get_fibos(self):
        fibos = []
        count = 1
        for _ in self.fibos:
            fibos.append(self.processed_data.get(['fr_{}'.format(count)][-1], None))
            count += 1
        return fibos
    
    def get_last_min_info(self):
        index = self.processed_data['min'].last_valid_index()
        value = self.processed_data['min'][index]
        return value, index
    
    def get_last_max_info(self):
        index = self.processed_data['max'].last_valid_index()
        value = self.processed_data['max'][index]
        return value, index