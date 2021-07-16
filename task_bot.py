import schedule
import time
import requests
import json

from datetime import datetime

time.sleep(60)

trade_period = "15m"

url = "http://127.0.0.1:7000/trades/bot/{}"

url8000 = "http://127.0.0.1:8000/trades/bot/{}"

payload = json.dumps({
  "principal_trade_period": trade_period,
  "money": 3700,
  "sl_percent": 0.015,
  "sl_period": 3,
  "population_min": 150,
  "population_max": 200,
  "individual_dna_length": 12,
  "individual_muatition_intensity": 180,
  "min_cod_ind_value": 2048,
  "max_cod_ind_value": -2048,
  "generations_ind": 250,
  "pair": "BNBBUSD"
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
  if ((min + 1) % 15) == 0: 
    requests.request("POST", url.format("evaluate"), headers=headers, data=payload) 
  

if trade_period == "15m":
  schedule.every().minute.at(":10").do(evaluate_15)
  schedule.every().hour.at(":01").do(train)
  while True:
      schedule.run_pending()
      time.sleep(10)
elif trade_period == "1h":
  schedule.every(1).hour.at(":57").do(evaluate)
  while True:
      schedule.run_pending()
      time.sleep(60)
