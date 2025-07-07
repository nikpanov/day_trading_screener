import pytest
import pandas as pd
from datetime import datetime


@pytest.fixture
def fake_fundamentals():
    return {
        "beta": 1.25,
        "market_cap": 950_000_000,
        "pe_ratio": 22.5,
        "sector": "Technology",
    }


@pytest.fixture
def fake_technicals():
    return {
        "RSI": 55.2,
        "MACD": 1.8,
        "volume": 1_200_000,
        "SMA_50": 210.0,
        "SMA_200": 190.0,
    }


@pytest.fixture
def fake_screener_cache(fake_fundamentals):
    return {
        "AAPL": fake_fundamentals,
        "MSFT": fake_fundamentals,
    }


@pytest.fixture
def fake_premarket_cache():
    return {
        "AAPL": 0.023,
        "MSFT": -0.012,
    }


@pytest.fixture
def sample_price_series():
    return pd.Series([100, 102, 104, 106, 108, 110], name="Close")


@pytest.fixture
def fake_run_metadata():
    return {
        "run_id": 1,
        "timestamp": datetime(2025, 7, 7, 9, 30),
        "tickers": ["AAPL", "MSFT"],
        "notes": "Test run",
    }