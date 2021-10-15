from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from apps.trades.binance.client import Client
from apps.trades.binance.websockets import BinanceSocketManager
from apps.trades.binance.exceptions import BinanceAPIException

from apps.trades.ia.bot import (
    TraderBot
)

from apps.trades.models import Individual as IndividualModel


import traceback

from django.views.decorators.csrf import csrf_exempt

from threading import Thread
import time

import datetime
import json

from django.utils.timezone import make_aware

from apps.trades.ia.basic_trading.trader import (
    TraderBTCBUSD,
    TraderETHBUSD,
    TraderADABUSD,
    TraderBNBBUSD,
    TraderBUSDUSDT,
    TraderSHIBBUSD
)

from apps.trades.ia.utils.strategies.strategies import Strategy

# Exchange endpoints

PAIR_INFO = {
    "BTCBUSD": {
        "trader_class": TraderBTCBUSD,
        "coin1": "BUSD",
        "coin2": "BTC"
    },
    "BNBBUSD": {
        "trader_class": TraderBNBBUSD,
        "coin1": "BUSD",
        "coin2": "BNB"
    },
    "ETHBUSD": {
        "trader_class": TraderETHBUSD,
        "coin1": "BUSD",
        "coin2": "ETH"
    },
    "ADABUSD": {
        "trader_class": TraderADABUSD,
        "coin1": "BUSD",
        "coin2": "ADA"
    },
    "BUSDUSDT": {
        "trader_class": TraderBUSDUSDT,
        "coin1": "BUSD",
        "coin2": "USDT"
    },
    "SHIBBUSD": {
        "trader_class": TraderSHIBBUSD,
        "coin1": "BUSD",
        "coin2": "SHIB"
    }
}


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
def train(request):
    print("++++++++++++++++++++++++++++++++++++++++++++")
    print(datetime.datetime.now())
    fields = [
        "principal_trade_period",
        "money",
        "sl_percent",
        "sl_period",
        "population_min",
        "population_max",
        "individual_dna_length",
        "individual_muatition_intensity",
        "min_cod_ind_value",
        "max_cod_ind_value",
        "generations_ind",
        "pair",
        "periods_environment"
    ]
    fields_to_func = {}
    body = json.loads(request.body.decode('utf-8'))
    for f in fields:
        if f not in body:
            return JsonResponse({'message': f'Falta campo {f}'},
                                status=400)
        fields_to_func[f"_{f}"] = body[f]
        
    PIC = PAIR_INFO[fields_to_func["_pair"]]
    fields_to_func["_trader_class"] = PIC["trader_class"]
    fields_to_func["_coin1"] = PIC["coin1"]
    fields_to_func["_coin2"] = PIC["coin2"]

    today = make_aware(datetime.datetime.now())
    last_date = today - datetime.timedelta(seconds=60 * 60 * 6)

    ie = IndividualModel.objects.filter(
        length=body["individual_dna_length"],
        min_value=body["min_cod_ind_value"],
        max_value=body["max_cod_ind_value"],
        pair=body["pair"],
        temp=body["principal_trade_period"],
        created_date__gte=last_date,
        percent=body["sl_percent"],
        percent_divisor_increment=body["sl_period"]
    ).exists()
    ie = False
    try:
        if not ie:
            btb = TraderBot(
                **fields_to_func
            )
            btb.eval_function_with_genetic_algorithm()
            btb.set_info_to_invest()
            btb.graph_data()
            return JsonResponse({'message': "Entrenamiento exitoso"}, status=200)
        return JsonResponse({'message': "Entrenamiento reciente con las mismas caracteristicas"}, status=200)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'message': "Entrenamiento fallido"}, status=500)


@csrf_exempt
def evaluate(request):
    print("++++++++++++++++++++++++++++++++++++++++++++")
    print(datetime.datetime.now())
    fields = [
        "principal_trade_period",
        "money",
        "sl_percent",
        "sl_period",
        "population_min",
        "population_max",
        "individual_dna_length",
        "individual_muatition_intensity",
        "min_cod_ind_value",
        "max_cod_ind_value",
        "generations_ind",
        "pair",
        "periods_environment"
    ]
    fields_to_func = {}
    body = json.loads(request.body.decode('utf-8'))
    for f in fields:
        if f not in body:
            return JsonResponse({'message': f'Falta campo {f}'},
                                status=400)
        fields_to_func[f"_{f}"] = body[f]
        
    PIC = PAIR_INFO[fields_to_func["_pair"]]
    fields_to_func["_trader_class"] = PIC["trader_class"]
    fields_to_func["_coin1"] = PIC["coin1"]
    fields_to_func["_coin2"] = PIC["coin2"]
    try:
        btb = TraderBot(
            **fields_to_func
        )
        btb.eval_function_with_genetic_algorithm_last_individual()
        btb.set_info_to_invest()
        btb.graph_data()
        btb.invest_based_ag()
        return JsonResponse({'message': "Entrenamiento exitoso"}, status=200)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'message': "Entrenamiento fallido"}, status=500)

@csrf_exempt
def async_evaluate(request):
    if request.method == "POST":
        try:
            t = Thread(target=evaluate, args=(request, ))
            t.start()
            return JsonResponse({'message': "Evaluacion exitosa"}, status=200)
        except Exception:
            traceback.print_exc()
            return JsonResponse({'message': "Evaluacion fallida"}, status=500)
    else:
        return JsonResponse({'message': 'Método no permitido'}, status=405)


@csrf_exempt
def async_train(request):
    if request.method == "POST":
        try:
            t = Thread(target=train, args=(request, ))
            t.start()
            return JsonResponse({'message': "Entrenamiento exitoso"}, status=200)
        except Exception:
            traceback.print_exc()
            return JsonResponse({'message': "Entrenamiento fallido"}, status=500)
    else:
        return JsonResponse({'message': 'Método no permitido'}, status=405)
    
@csrf_exempt
def evaluate_no_ai(request):
    print("++++++++++++++++++++++++++++++++++++++++++++")
    print(datetime.datetime.now())
    fields = [
        "principal_trade_period",
        "money",
        "sl_percent",
        "sl_period",
        "pair",
        "periods_environment",
        "interval"
    ]
    fields_to_func = {}
    body = json.loads(request.body.decode('utf-8'))
    for f in fields:
        if f not in body:
            return JsonResponse({'message': f'Falta campo {f}'},
                                status=400)
        fields_to_func[f"_{f}"] = body[f]
        
    PIC = PAIR_INFO[fields_to_func["_pair"]]
    fields_to_func["_trader_class"] = PIC["trader_class"]
    fields_to_func["_coin1"] = PIC["coin1"]
    fields_to_func["_coin2"] = PIC["coin2"]

    try:
        btb = Strategy(
            **fields_to_func
        )
        btb.eval_function_wit_last_individual()
        btb.graph_data()
        btb.invest()
        return JsonResponse({'message': "Entrenamiento exitoso"}, status=200)
    except Exception:
        traceback.print_exc()
        return JsonResponse({'message': "Entrenamiento fallido"}, status=500)