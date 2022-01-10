import schedule
import time
import requests
import json

from datetime import datetime

time.sleep(60)

trade_period = "1h"

url = "http://127.0.0.1:7000/trades/bot/{}"

url8000 = "http://127.0.0.1:8001/trades/bot/{}"

payload = json.dumps({
  "principal_trade_period": trade_period,
  "money": 10000,
  "sl_percent": 0.4,
  "sl_period": 0.0004,
  "population_min": 10,
  "population_max": 20,
  "individual_dna_length": 256,
  "individual_muatition_intensity": 128,
  "min_cod_ind_value": -1,
  "max_cod_ind_value": 1,
  "generations_ind": 1000,
  "pair": "BNBBUSD",
  "periods_environment": 500,
  "interval": 8,
  "variables": 0,
  "socialmedia": False
})

headers = {
  'Content-Type': 'application/json'
}

def train():
  requests.request("POST", url8000.format("train"), headers=headers, data=payload) 
  
train()

def evaluate():
  requests.request("POST", url.format("evaluate"), headers=headers, data=payload) 
  
def evaluate_15():
  n = datetime.now()
  t = n.timetuple()
  y, m, d, h, min, sec, wd, yd, i = t
  if ((min ) % 15) == 0: 
    requests.request("POST", url.format("evaluate"), headers=headers, data=payload) 
  

if trade_period == "15m":
  schedule.every().minute.at(":03").do(evaluate_15)
  schedule.every().hour.at(":01").do(train)
  while True:
      schedule.run_pending()
      time.sleep(10)
elif trade_period == "1h":
  schedule.every(1).hour.at(":57").do(evaluate)
  while True:
      schedule.run_pending()
      time.sleep(60)
elif trade_period == "4h":
  schedule.every(4).hour.at(":01").do(evaluate)
  while True:
      schedule.run_pending()
      time.sleep(60)

