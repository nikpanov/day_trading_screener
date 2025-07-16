
import os
import requests
from dotenv import load_dotenv
from db import get_connection
from datetime import datetime
import pandas as pd
from utils.filters import is_bullish 
from utils.logger import setup_logger
from utils.ratelimiter import RateLimiter
from utils.retry import retry_with_backoff, retry_on_429

# 5 requests per second
screener_limiter = RateLimiter(4, 1)
historical_limiter = RateLimiter(4, 1)
tech_limiter = RateLimiter(4, 1)
fund_limiter = RateLimiter(4, 1)
premarket_limiter = RateLimiter(4, 1)
vwap_limiter = RateLimiter(4, 1)

logger = setup_logger()

# Load environment variables from .env
load_dotenv()
FMP_API_KEY = os.getenv("FMP_API_KEY")

BASE_URL = "https://financialmodelingprep.com/api/v3"

@retry_with_backoff(logger=logger)
@retry_on_429(logger=logger) 
def fetch_historical_prices(symbol: str, interval: str = "1day", limit: int = 100):
    historical_limiter.wait()
    url = f"{BASE_URL}/historical-price-full/{symbol}?apikey={FMP_API_KEY}&serietype=line"
    response = requests.get(url)
    if response.ok:
        data = response.json().get("historical", [])[:limit]
        return pd.DataFrame(data).sort_values("date")
    return None

@retry_with_backoff(logger=logger)
@retry_on_429(logger=logger) 
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

@retry_with_backoff(logger=logger)
@retry_on_429(logger=logger) 
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

@retry_with_backoff(logger=logger)
@retry_on_429(logger=logger) 
def fetch_core_screener(limit=500, mode="default"):
    screener_limiter.wait()
    base_url = f"{BASE_URL}/stock-screener"

    # Default base params
    params = {
        "apikey": FMP_API_KEY,
        "exchange": "NASDAQ,NYSE",
        "limit": limit
    }

    if mode == "default":
        params.update({
            "volumeMoreThan": 500_000,
            "priceMoreThan": 1,
            "changeMoreThan": 2,
            "sort": "volume"  # Or omit for raw order
        })
    elif mode == "final":
        params.update({
            "volumeMoreThan": 1_000_000,
            "priceMoreThan": 5,
            "changeMoreThan": 3,
            "sort": "change"  # Top movers by % gain
        })
    elif mode == "debug":
        params["limit"] = 5  # quick testing
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Screener API Error: {e}")
        logger.error(f"Screener API Error: {e}")
        return []

@retry_with_backoff(logger=logger)
@retry_on_429(logger=logger) 
def fetch_technicals(symbol: str) -> dict | None:
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
            print(f"No data for {symbol} {indicator}")
            logger.warning(f"No data for {symbol} {indicator}")
            return None
        except Exception as e:
            print(f"API error for {symbol} {indicator}: {e}")
            logger.error(f"API error for {symbol} {indicator}: {e}")
            return None

    indicators = {
        "rsi14": get_tech("rsi", 14),
        "ema20": get_tech("ema", 20),
        "ema50": get_tech("ema", 50),
        "vwap": fetch_vwap_from_eod(symbol)
    }

    return None if all(v is None for v in indicators.values()) else indicators

@retry_with_backoff(logger=logger)
@retry_on_429(logger=logger) 
def fetch_vwap_from_eod(symbol: str) -> float | None:
    vwap_limiter.wait()
    url = "https://financialmodelingprep.com/stable/historical-price-eod/full"
    params = {
        "symbol": symbol,
        "apikey": FMP_API_KEY
    }

    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        data = r.json()

        historical = data.get("historical", []) if isinstance(data, dict) else data
        if historical and isinstance(historical[0], dict) and "vwap" in historical[0]:
            return float(historical[0]["vwap"])

        print(f"No VWAP found in EOD data for {symbol}")
        logger.warning(f"No VWAP found in EOD data for {symbol}")
        return None

    except Exception as e:
        print(f"Error fetching EOD VWAP for {symbol}: {e}")
        logger.error(f"Error fetching EOD VWAP for {symbol}: {e}")
        return None
