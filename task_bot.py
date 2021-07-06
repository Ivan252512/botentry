import schedule
import time
import requests
import json

from datetime import datetime

time.sleep(60)

trade_period = "1h"

url = "http://127.0.0.1:7000/trades/bot/{}"

payload = json.dumps({
  "principal_trade_period": trade_period,
  "money": 2500,
  "sl_percent": 0.02,
  "sl_period": 2,
  "population_min": 1000,
  "population_max": 5000,
  "individual_dna_length": 8,
  "individual_muatition_intensity": 12,
  "min_cod_ind_value": 1024,
  "max_cod_ind_value": -1024,
  "generations_ind": 150
})

headers = {
  'Content-Type': 'application/json'
}

def train():
  requests.request("POST", url.format("train_btc"), headers=headers, data=payload) 
  
train()

def evaluate():
  requests.request("POST", url.format("evaluate_btc"), headers=headers, data=payload) 
  
def evaluate_15():
  n = datetime.now()
  t = n.timetuple()
  y, m, d, h, min, sec, wd, yd, i = t
  if ((min + 1) % 15) == 0: 
    requests.request("POST", url.format("evaluate_btc"), headers=headers, data=payload) 
  

if trade_period == "15m":
  schedule.every().minute.at(":50").do(evaluate_15)
  while True:
      schedule.run_pending()
      time.sleep(5)
elif trade_period == "1h":
  schedule.every().hour.at(":55").do(evaluate)
  while True:
      schedule.run_pending()
      time.sleep(60)
