import os
import requests
from dotenv import load_dotenv
from db import get_connection
from datetime import datetime
import pandas as pd
from utils.filters import is_bullish   

from utils.logger import setup_logger


logger = setup_logger()

# Load environment variables from .env
load_dotenv()
FMP_API_KEY = os.getenv("FMP_API_KEY")

BASE_URL = "https://financialmodelingprep.com/api/v3"


def fetch_core_screener(limit=50):
    """
    Fetch stocks that pass core day trading filters.
    """
    url = f"{BASE_URL}/stock-screener"
    params = {
        "apikey": FMP_API_KEY,
        "volumeMoreThan": 500000,
        "priceMoreThan": 1,
        "changeMoreThan": 2,
        "exchange": "NASDAQ,NYSE",
        "limit": limit
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"❌ Screener API Error: {e}")
        logger.error(f"Screener API Error: {e}")
        return []


def fetch_technicals(symbol: str) -> dict | None:
    """
    Fetch RSI14, EMA20, EMA50, VWAP using FMP's stable endpoint.
    Returns a dictionary or None if all data is missing.
    """
    def get_tech(indicator: str, period_length=None, timeframe="15min"):
        url = f"https://financialmodelingprep.com/stable/technical-indicators/{indicator}"
        
        params = {
            "apikey": FMP_API_KEY,
            "symbol": symbol,
            "timeframe": timeframe
        }
        if period_length:
            params["periodLength"] = period_length

        try:
            r = requests.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, list) and data:
                return float(data[0].get(indicator))
            print(f"⚠️ No data for {symbol} {indicator}")
            logger.warning(f"No data for {symbol} {indicator}")
            return None
        except Exception as e:
            print(f"⚠️ API error for {symbol} {indicator}: {e}")
            logger.error(f"API error for {symbol} {indicator}: {e}")
            return None

    indicators = {
        "rsi14": get_tech("rsi", 14),
        "ema20": get_tech("ema", 20),
        "ema50": get_tech("ema", 50),
        "vwap": fetch_vwap_from_eod(symbol)  # No periodLength needed
    }

    if all(v is None for v in indicators.values()):
        return None
    return indicators

def fetch_vwap_from_eod(symbol: str) -> float | None:
    """
    Fetches latest daily VWAP value from EOD full price history.
    """
    url = f"https://financialmodelingprep.com/stable/historical-price-eod/full"
    params = {
        "symbol": symbol,
        "apikey": FMP_API_KEY
    }

    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()

        if isinstance(data, dict):
            historical = data.get("historical", [])
        elif isinstance(data, list):
            historical = data  # just assume it's the full list
        else:
            print(f"⚠️ Unexpected response type for {symbol}: {type(data)}")
            logger.error(f"Unexpected response type for {symbol}: {type(data)}")
            return None

        if historical and isinstance(historical[0], dict) and "vwap" in historical[0]:
            return float(historical[0]["vwap"])

        print(f"⚠️ No VWAP found in EOD data for {symbol}")
        logger.warning(f"No VWAP found in EOD data for {symbol}")
        return None

    except Exception as e:
        print(f"⚠️ Error fetching EOD VWAP for {symbol}: {e}")
        logger.error(f"Error fetching EOD VWAP for {symbol}: {e}")
        return None



# Debug/test runner
if __name__ == "__main__":
    results = fetch_core_screener(limit=5)
    print(f"✅ Retrieved {len(results)} stocks")
    logger.info(f"Retrieved {len(results)} stocks from screener")

    # Add these before your for-loop
    all_results = []
    run_timestamp = datetime.utcnow()

    # After fetching each stock:
    for stock in results:
        symbol = stock["symbol"]
        name = stock.get("companyName", "")
        price = stock.get("price")

        print(f"\n🔍 {symbol} - {name}")
        indicators = fetch_technicals(symbol)

        if not indicators:
            print("⚠️ No technical data — skipping.")
            logger.warning(f"No technical data for {symbol} — skipping.")
            continue

        bullish = is_bullish(price, indicators)
        if bullish:
            print("✅ Bullish signal!")
            logger.info(f"Bullish signal for {symbol} at {run_timestamp}")

        # collect result
        all_results.append({
            "symbol": symbol,
            "company_name": name,
            "price": price,
            **indicators,
            "is_bullish": bullish,
            "timestamp": run_timestamp
        })

        print(f"📊 Technicals: {techs}")
        logger.info(f"Technical indicators for {symbol}: {indicators} completed")