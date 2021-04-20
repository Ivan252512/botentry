import matplotlib.pyplot as plt
import mplfinance as fplt
import pandas as pd
import matplotlib.dates as mpdates
import datetime

from apps.trades.binance.client import Client

# https://www.geeksforgeeks.org/plot-candlestick-chart-using-mplfinance-module-in-python/
# https://coderzcolumn.com/tutorials/data-science/candlestick-chart-in-python-mplfinance-plotly-bokeh

class Graphic:

    def __init__(self, _raw_data, _pair):
        self.raw_data = _raw_data
        self.pair = _pair
        self.processed_data = None
        self.ma = None 
        self.graphic = None 
        self.indicators = []
        
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
        self.processed_data['ma_{}'.format(_periods)] = self.processed_data.rolling(window=_periods)['open'].mean()
        self.indicators.append('ma_{}'.format(_periods))
        
    def calculate_fibonacci_retractament(self):
        fibo_levels = [0.382, 0.500, 0.618, 1]
        count = 1
        for fb in fibo_levels:
            max = self.processed_data['open'].max()
            min = self.processed_data['open'].min() 
            self.processed_data['fr_{}'.format(count)] = [min + fb * (max - min) for _ in self.raw_data]
            self.indicators.append('fr_{}'.format(count) )
            count += 1
        
    def graph(self):
        subplots = []
        print(self.processed_data)
        for i in self.indicators:
            subplots.append(
                fplt.make_addplot(
                    self.processed_data[i],
                    type='line'
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
            addplot=subplots
        ) 
