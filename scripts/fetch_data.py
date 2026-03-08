#!/usr/bin/env python3
"""Fetch market data and write to data/latest.json"""

import json
import os
from datetime import datetime, timezone

import requests
import yfinance as yf

TICKERS = {
    "NQ": "NQ=F",
    "ES": "ES=F",
    "RTY": "RTY=F"
}

def fetch_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/?limit=1", timeout=10)
        d = r.json()
        score = int(d["data"][0]["value"])
        label = d["data"][0]["value_classification"]
        return {"score": score, "label": label}
    except Exception as e:
        print(f"Fear & Greed error: {e}")
        return None

def fetch_futures():
    results = {}
    for name, symbol in TICKERS.items():
        try:
            t = yf.Ticker(symbol)
            hist = t.history(period="5d")
            if hist.empty:
                continue
            curr = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[-2])
            chg = curr - prev
            pct = (chg / prev) * 100
            results[name] = {
                "price": round(curr, 2),
                "change": round(chg, 2),
                "changePct": round(pct, 4),
                "dayHigh": round(float(hist["High"].iloc[-1]), 2),
                "dayLow": round(float(hist["Low"].iloc[-1]), 2),
                "prevClose": round(prev, 2),
                "closes": [round(float(c), 2) for c in hist["Close"].tolist()]
            }
            print(f"{name}: {curr:.2f} ({pct:+.2f}%)")
        except Exception as e:
            print(f"{name} error: {e}")
    return results

def main():
    print("Fetching market data...")
    fg = fetch_fear_greed()
    futures = fetch_futures()
    
    data = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "fearGreed": fg,
        "futures": futures
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/latest.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Written to data/latest.json")
    print(f"Fear & Greed: {fg}")

if __name__ == "__main__":
    main()
