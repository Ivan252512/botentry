from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from apps.trades.binance.client import Client
from apps.trades.binance.websockets import BinanceSocketManager
from apps.trades.binance.exceptions import BinanceAPIException

from apps.trades.ia.bot import (
    BTCBUSDTraderBot
)

import traceback

from django.views.decorators.csrf import csrf_exempt

from threading import Thread
import time

# Exchange endpoints

def get_products(request):
    if request.method == "GET":
        client = Client()
        products = client.get_products()
        return JsonResponse({'message': products}, status=200)
    else:
        return JsonResponse({'message': 'Metodo no permitido'}, status=405)

def get_exchange_info(request):
    if request.method == "GET":
        client = Client()
        exchange_info = client.get_exchange_info()
        return JsonResponse({'message': exchange_info}, status=200)
    else:
        return JsonResponse({'message': 'Metodo no permitido'}, status=405)

def get_symbol_info(request, symbol):
    if request.method == "GET":
        client = Client()
        symbol_info = client.get_symbol_info(symbol)
        return JsonResponse({'message': symbol_info}, status=200)
    else:
        return JsonResponse({'message': 'Metodo no permitido'}, status=405)
    
def get_ping(request):
    if request.method == "GET":
        client = Client()
        ping = client.ping()
        return JsonResponse({'message': ping}, status=200)
    else:
        return JsonResponse({'message': 'Metodo no permitido'}, status=405)
    
def get_server_time(request):
    if request.method == "GET":
        client = Client()
        server_time = client.get_server_time()
        return JsonResponse({'message': server_time}, status=200)
    else:
        return JsonResponse({'message': 'Metodo no permitido'}, status=405)   
    

    
# Market Data endpoints

def get_all_tickers(request):
    if request.method == "GET":
        client = Client()
        all_tickers = client.get_all_tickers()
        return JsonResponse({'message': all_tickers}, status=200)
    else:
        return JsonResponse({'message': 'Metodo no permitido'}, status=405)
    

def get_orderbook_tickers(request):
    if request.method == "GET":
        client = Client()
        orderbook_tickers = client.get_orderbook_tickers()
        return JsonResponse({'message': orderbook_tickers}, status=200)
    else:
        return JsonResponse({'message': 'Metodo no permitido'}, status=405)
    
def get_orderbook(request, symbol):
    if request.method == "GET":
        client = Client()
        print(client.API_KEY, client.API_SECRET)
        orderbook = client.get_order_book(symbol=symbol)
        return JsonResponse({'message': orderbook}, status=200)
    else:
        return JsonResponse({'message': 'Metodo no permitido'}, status=405)
    
def get_recent_trades(request, symbol):
    if request.method == "GET":
        client = Client()
        recent_trades = client.get_recent_trades(symbol=symbol)
        return JsonResponse({'message': recent_trades}, status=200)
    else:
        return JsonResponse({'message': 'Metodo no permitido'}, status=405)
    
def get_historical_trades(request, symbol):
    if request.method == "GET":
        client = Client()
        historical_trades = client.get_historical_trades(symbol=symbol)
        return JsonResponse({'message': historical_trades}, status=200)
    else:
        return JsonResponse({'message': 'Metodo no permitido'}, status=405)
    
def get_aggregate_trades(request, symbol):
    if request.method == "GET":
        client = Client()
        aggregate_trades = client.get_aggregate_trades(symbol=symbol)
        return JsonResponse({'message': aggregate_trades}, status=200)
    else:
        return JsonResponse({'message': 'Metodo no permitido'}, status=405)
    
def get_klines(request, symbol, interval):
    if request.method == "GET":
        client = Client()
        klines = client.get_klines(symbol=symbol, interval=interval)
        return JsonResponse({'message': klines}, status=200)
    else:
        return JsonResponse({'message': 'Metodo no permitido'}, status=405)
    
def get_historical_klines(request, symbol, interval, start_str, end_str, limit):
    if request.method == "GET":
        client = Client()
        historical_klines = client.get_historical_klines(
            symbol=symbol,
            interval=interval,
            start_str=start_str,
            end_str=end_str,
            limit=limit
        )
        return JsonResponse({'message': historical_klines}, status=200)
    else:
        return JsonResponse({'message': 'Metodo no permitido'}, status=405)
       
# User Account

def get_account(request):
    if request.method == "GET":
        client = Client()
        account = client.get_account()
        return JsonResponse({'message': account}, status=200)
    else:
        return JsonResponse({'message': 'Metodo no permitido'}, status=405)

# Bot Endpoints

@csrf_exempt
def train_btc(request):
    try:
        btb = BTCBUSDTraderBot(
            _principal_trade_period="15m"
        )
        btb.eval_function_with_genetic_algorithm()
        btb.set_info_to_invest()
        btb.cancel_all_open_orders()
        btb.invest_based_ag()
        btb.graph_data()
        return JsonResponse({'message': "Entrenamiento exitoso"}, status=200)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'message': "Entrenamiento fallido"}, status=500)

@csrf_exempt
def evaluate_btc(request):
    try:
        btb = BTCBUSDTraderBot(
            _principal_trade_period="15m"
        )
        btb.eval_function_with_genetic_algorithm_last_individual()
        btb.set_info_to_invest()
        btb.invest_based_ag()
        btb.graph_data()
        return JsonResponse({'message': "Entrenamiento exitoso"}, status=200)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'message': "Entrenamiento fallido"}, status=500)
    
def async_evaluate(request):
    minutos = 0
    while True:
        try:
            if minutos == 0:
                t = Thread(target=train_btc, args=(request, ))
                t.start()
            else:
                t = Thread(target=evaluate_btc, args=(request, ))
                t.start()
        except Exception:
            traceback.print_exc()
        minutos += 15
        if minutos >= 6 * 4 * 15:
            minutos = 0
        time.sleep(15 * 60)
    
@csrf_exempt
def run_bot(request):
    if request.method == "GET":
        try:
            t = Thread(target=async_evaluate, args=(request, ))
            t.start()
            return JsonResponse({'message': "Entrenamiento exitoso"}, status=200)
        except Exception:
            traceback.print_exc()
            return JsonResponse({'message': "Entrenamiento fallido"}, status=500)
    else:
        return JsonResponse({'message': 'Método no permitido'}, status=405)
