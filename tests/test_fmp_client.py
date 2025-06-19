import pytest
from api.fmp_client import fetch_technicals

@pytest.mark.parametrize("symbol", ["AAPL", "MSFT", "NVDA"])
def test_fetch_technicals_valid_symbols(symbol):
    indicators = fetch_technicals(symbol)

    assert isinstance(indicators, dict), "fetch_technicals should return a dictionary"
    assert set(indicators.keys()) == {"vwap", "ema20", "ema50", "rsi14"}

    # We don’t expect all indicators to be non-None, but at least one should be present for valid tickers
    assert any(val is not None for val in indicators.values()), f"No data fetched for {symbol}"
