import pytest
import pandas as pd
from backtester import simulate_trade

def test_simulate_trade_basic():
    price_data = pd.DataFrame({
        "date": pd.date_range("2023-01-01", periods=5),
        "close": [100, 105, 110, 108, 112],
    })

    buy_price = 100
    sell_price, sell_date, gain_pct, hold_days, result = simulate_trade(price_data, buy_price)

    assert isinstance(sell_price, (float, int))
    assert result in ("win", "loss", "neutral")
