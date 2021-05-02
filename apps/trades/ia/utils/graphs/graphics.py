import matplotlib.pyplot as plt
import mplfinance as fplt
import pandas as pd
import matplotlib.dates as mpdates
import datetime

import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.stats import linregress

from apps.trades.binance.client import Client

# https://www.geeksforgeeks.org/plot-candlestick-chart-using-mplfinance-module-in-python/
# https://coderzcolumn.com/tutorials/data-science/candlestick-chart-in-python-mplfinance-plotly-bokeh

class Graphic:

    def __init__(self, _raw_data, _pair):
        self.raw_data = _raw_data
        self.length = len(_raw_data)
        self.pair = _pair
        self.processed_data = None
        self.ma = None 
        self.graphic = None 
        self.indicators = []
        self.maxs_columns = []
        self.mins_columns = []
        
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
        
        self.processed_data = df2
        
    def calculate_moving_average(self, _periods):
        self.processed_data['ma_{}'.format(_periods)] = self.processed_data.rolling(window=_periods)['low'].mean()
        self.indicators.append('ma_{}'.format(_periods))
        
    def calculate_exponential_moving_average(self, _periods):
        pass
        
    def calculate_fibonacci_retracement(self):
        fibo_levels = [0, 0.236, 0.382, 0.500, 0.618, 0.786, 1, 1.618]
        count = 1
        for fb in fibo_levels:
            max = self.processed_data['high'].max()
            min = self.processed_data['low'].min() 
            self.processed_data['fr_{}'.format(count)] = [min + fb * (max - min) for _ in self.raw_data]
            self.indicators.append('fr_{}'.format(count))
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
        self.indicators.append('fd_low_{}'.format(_sigma_gaussian_filter))
        self.processed_data['d2_low_{}'.format(_sigma_gaussian_filter)] = np.gradient(np.gradient(filtered_data_low))
        self.indicators.append('d2_low_{}'.format(_sigma_gaussian_filter))
        self.processed_data['fd_high_{}'.format(_sigma_gaussian_filter)] = filtered_data_high
        self.indicators.append('fd_high_{}'.format(_sigma_gaussian_filter))
        self.processed_data['d2_high_{}'.format(_sigma_gaussian_filter)] = np.gradient(np.gradient(filtered_data_high))
        self.indicators.append('d2_high_{}'.format(_sigma_gaussian_filter))
        #self._put_min_respectly_in_data_df('low', 'd2_low_{}'.format(_sigma_gaussian_filter), _sigma_gaussian_filter)
        #self._put_max_respectly_in_data_df('high', 'd2_high_{}'.format(_sigma_gaussian_filter),_sigma_gaussian_filter)
        
    def _put_min_respectly_in_data_df(self, _df, _df2, _sigma_gaussian_filter):
        df = self.processed_data
        self.processed_data['min_correspondent_{}_{}'.format(_df ,_df2)] = df[_df][(df[_df2].shift(1) < df[_df2]) & (df[_df2].shift(-1) < df[_df2])]
        self.indicators.append('min_correspondent_{}_{}'.format(_df, _df2))
        
        dates_intervals = np.array([i for i in range(self.length)])
        mask = ~np.isnan(dates_intervals[400:]) & ~np.isnan(self.processed_data['min_correspondent_{}_{}'.format(_df ,_df2)][400:])        
        reg = linregress(
            x=dates_intervals[400:][mask],
            y=self.processed_data['min_correspondent_{}_{}'.format(_df ,_df2)][400:][mask]
        )
        self.processed_data['reg_mn_correspondent_{}_{}'.format(_df ,_df2)] = reg[0] * dates_intervals + reg[1]
        self.indicators.append('reg_mn_correspondent_{}_{}'.format(_df ,_df2))
    
    def _put_max_respectly_in_data_df(self, _df, _df2, _sigma_gaussian_filter):
        df = self.processed_data
        self.processed_data['max_correspondent_{}_{}'.format(_df, _df2)] = df[_df][(df[_df2].shift(1) > df[_df2]) & (df[_df2].shift(-1) > df[_df2])]
        self.indicators.append('max_correspondent_{}_{}'.format(_df, _df2))

        dates_intervals = np.array([i for i in range(self.length)])
        mask = ~np.isnan(dates_intervals[400:]) & ~np.isnan(self.processed_data['max_correspondent_{}_{}'.format(_df ,_df2)][400:])        
        reg = linregress(
            x=dates_intervals[400:][mask],
            y=self.processed_data['max_correspondent_{}_{}'.format(_df ,_df2)][400:][mask]
        )
        self.processed_data['reg_mx_correspondent_{}_{}'.format(_df ,_df2)] = reg[0] * dates_intervals + reg[1]
        self.indicators.append('reg_mx_correspondent_{}_{}'.format(_df ,_df2))
        
    def get_processed_data(self):
        return self.processed_data.copy()
    
    def get_normalized_processed_data(self):
        df = self.processed_data.copy()
        result = self.processed_data.copy()
        for feature_name in df.columns:
            max_value = df[feature_name].max()
            min_value = df[feature_name].min()
            result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
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
            if "max" in i:
                subplots.append(
                    fplt.make_addplot(
                        self.processed_data[i],
                        type='scatter',
                        markersize=50 * count_max,
                        marker='v'
                    )
                )
                count_max += 1
            elif "min" in i:
                subplots.append(
                    fplt.make_addplot(
                        self.processed_data[i],
                        type='scatter',
                        markersize=50 * count_min,
                        marker='^'
                    )
                )
                count_min += 1
            else:
                subplots.append(
                    fplt.make_addplot(
                        self.processed_data[i],
                        type='line',
                    )
                )

        fplt.plot(
            self.processed_data,
            type='candle',
            style='charles',
            title=self.pair,
            ylabel='Price ($)',
            volume=True,
            ylabel_lower='Shares\nTraded',
            ylim=(0, self.processed_data['high'].max()*1.7),
            addplot=subplots
        ) 
