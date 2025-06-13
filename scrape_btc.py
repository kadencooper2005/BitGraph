import requests
import pandas as pd
import time

API_KEY = "f33b582d4e2a6267324ecc5b3fdcbcc26097916fe629ea5c1ec42270f46c63ff"

def fetch_data(limit=2000, to_ts=None):
    url = "https://min-api.cryptocompare.com/data/v2/histoday"
    params = {
        "fsym": "BTC",
        "tsym": "USD",
        "limit": limit,
        "toTs": to_ts,
        "api_key": API_KEY
    }
    res = requests.get(url, params=params)
    return res.json()["Data"]["Data"]

# Fetch 4000 days in two calls
data = fetch_data(limit=2000)
data2 = fetch_data(limit=2000, to_ts=data[0]["time"])
combined = data2 + data

df = pd.DataFrame(combined)
df["time"] = pd.to_datetime(df["time"], unit="s")
df = df[["time", "open", "high", "low", "close", "volumefrom", "volumeto"]]
df.to_csv("btc_ohlcv.csv", index=False)

print("Data saved to file")