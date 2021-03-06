from django.urls import path
from apps.trades import views

urlpatterns = [
    
    # Exchange Endpoints
    path('exchange/get_products/', views.get_products, name='exchange-get-products'),
    path('exchange/get_exchange_info/', views.get_exchange_info, name='exchange-get-exchange-info'),
    path('exchange/get_symbol_info/<str:symbol>', views.get_symbol_info, name='exchange-get-symbol-info'),
    
    # General Endpoints
    path('exchange/get_ping/', views.get_ping, name='exchange-get-ping'),
    path('exchange/get_server_time/', views.get_server_time, name='exchange-get-servertime'),
    
    # Market Data Endpoints
    path('exchange/get_all_tickers', views.get_all_tickers, name='exchange-get-all-tickers'),
    path('exchange/get_orderbook_tickers', views.get_orderbook_tickers, name='exchange-get-orderbook-tickers'),
    path('exchange/get_orderbook/<str:symbol>', views.get_orderbook, name='exchange-get-orderbook'),
    path('exchange/get_recent_trades/<str:symbol>', views.get_recent_trades, name='exchange-get-recent-trades'),
    path('exchange/get_historical_trades/<str:symbol>', views.get_historical_trades, name='exchange-get-historical-trades'),
    path('exchange/get_aggregate_trades/<str:symbol>', views.get_aggregate_trades, name='exchange-get-aggregate-trades'),
    path('exchange/get_klines/<str:symbol>/<str:interval>', views.get_klines, name='exchange-get-klines'),   
    path('exchange/get_historical_klines/<str:symbol>/<str:interval>/<str:start_str>/<str:end_str>', views.get_historical_klines, name='exchange-get-historical-klines'),   
    
    # User Account  
    path('exchange/get_account', views.get_account, name='exchange-get-account-info'),
    
    # Bot
    # With AG
    path('bot/train', views.async_train, name='train'),
    path('bot/evaluate', views.evaluate, name='evaluate'),
    path('bot/test_post_to_facebook', views.test_post_to_facebook, name='test_post_to_facebook'),
    path('bot/futures_create_order', views.futures_create_order, name='futures_create_order'),
    
    # Without AG
    path('bot/evaluate_no_ai', views.evaluate_no_ai, name='evaluate_no_ai'),
    
    
]
