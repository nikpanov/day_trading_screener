import os
import requests
from dotenv import load_dotenv
from db import get_connection
from datetime import datetime
import pandas as pd
from utils.filters import is_bullish 
from utils.logger import setup_logger
from utils.ratelimiter import RateLimiter
from utils.retry import retry_with_backoff

# 5 requests per second
screener_limiter = RateLimiter(5, 1)
historical_limiter = RateLimiter(5, 1)
tech_limiter = RateLimiter(5, 1)
fund_limiter = RateLimiter(5, 1)
premarket_limiter = RateLimiter(5, 1)
vwap_limiter = RateLimiter(5, 1)

logger = setup_logger()

# Load environment variables from .env
load_dotenv()
FMP_API_KEY = os.getenv("FMP_API_KEY")

BASE_URL = "https://financialmodelingprep.com/api/v3"

# new
def fetch_historical_prices(symbol: str, interval: str = "1day", limit: int = 100):
    historical_limiter.wait()
    api_key = os.getenv("FMP_API_KEY")
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?apikey={api_key}&serietype=line"
    response = requests.get(url)
    if response.ok:
        data = response.json().get("historical", [])[:limit]
        return pd.DataFrame(data).sort_values("date")
    return None

def fetch_fundamentals(symbol):
    fund_limiter.wait()

    try:
        url = f"{BASE_URL}/profile/{symbol}?apikey={FMP_API_KEY}"
        response = requests.get(url)
        data = response.json()
        if isinstance(data, list) and data:
            item = data[0]
            return {
                "beta": item.get("beta"),
                "market_cap": item.get("mktCap"),
            }
    except Exception as e:
        print(f"Error fetching fundamentals for {symbol}: {e}")
    return {}

def fetch_pre_market_change(symbol):
    premarket_limiter.wait()
    try:
        url = f"{BASE_URL}/quote/{symbol}?apikey={FMP_API_KEY}"
        response = requests.get(url)
        data = response.json()
        if isinstance(data, list) and data:
            item = data[0]
            return item.get("changesPercentage")
    except Exception as e:
        print(f"Error fetching pre-market change for {symbol}: {e}")
    return None

def fetch_core_screener(limit=50):
    """
    Fetch stocks that pass core day trading filters.
    """
    screener_limiter.wait()
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
    tech_limiter.wait()

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
    vwap_limiter.wait()
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