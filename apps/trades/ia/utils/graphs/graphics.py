import matplotlib.pyplot as plt
from mplfinance import candlestick_ohlc
import pandas as pd
import matplotlib.dates as mpdates

from apps.trades.binance.client import Client

# https://www.geeksforgeeks.org/plot-candlestick-chart-using-mplfinance-module-in-python/
# https://coderzcolumn.com/tutorials/data-science/candlestick-chart-in-python-mplfinance-plotly-bokeh

class Graphic:

    def __init__(self):
        self.data = None
        self.graph = None 
        self.client = Client()
        

    def graph_only