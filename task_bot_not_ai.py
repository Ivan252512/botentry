import schedule
import time
import requests
import json

from datetime import datetime

time.sleep(60)

trade_period = "15m"

url = "http://127.0.0.1:7000/trades/bot/{}"

url8000 = "http://127.0.0.1:8001/trades/bot/{}"

payload = json.dumps({
  "principal_trade_period": trade_period,
  "money": 20,
  "sl_percent": 0.05,
  "sl_period": 0.001,
  "pair": "BTCBUSD",
  "periods_environment": 500,
  "interval": 10
})

headers = {
  'Content-Type': 'application/json'
}

def evaluate():
  requests.request("POST", url.format("evaluate_no_ai"), headers=headers, data=payload) 
  
def evaluate_15():
  n = datetime.now()
  t = n.timetuple()
  y, m, d, h, min, sec, wd, yd, i = t
  if ((min ) % 15) == 0: 
    requests.request("POST", url.format("evaluate_no_ai"), headers=headers, data=payload) 
  

if trade_period == "15m":
  schedule.every().minute.at(":03").do(evaluate_15)
  while True:
      schedule.run_pending()
      time.sleep(10)
elif trade_period == "1h":
  schedule.every(1).hour.at(":57").do(evaluate)
  while True:
      schedule.run_pending()
      time.sleep(60)
