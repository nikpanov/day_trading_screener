import pytest
from unittest.mock import patch, MagicMock
from db.cache import upsert_screener_cache, upsert_premarket_cache

@patch("db.cache.get_connection")
def test_upsert_screener_cache_executes_sql(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    mock_get_conn.return_value = mock_conn

    data = {
        "symbol": "AAPL",
        "company_name": "Apple Inc.",
        "price": 185.5,
        "rsi14": 55.2,
        "ema20": 182.1,
        "ema50": 178.9,
        "vwap": 183.3,
        "is_bullish": True,
        "failure_reason": None,
        "timestamp": "2025-07-07 13:30:00"
    }

    upsert_screener_cache(data)

    mock_cursor.execute.assert_called_once()
    args, kwargs = mock_cursor.execute.call_args
    assert "INSERT INTO day_trading_screener.screener_cache" in args[0]
    assert args[1]["symbol"] == "AAPL"
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("db.cache.get_connection")
def test_upsert_premarket_cache_executes_sql(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    mock_get_conn.return_value = mock_conn

    upsert_premarket_cache("MSFT", 0.042)

    mock_cursor.execute.assert_called_once()
    sql, params = mock_cursor.execute.call_args[0]
    assert "INSERT INTO day_trading_screener.premarket_cache" in sql
    assert params[0] == "MSFT"
    assert abs(params[1] - 0.042) < 1e-6
    mock_conn.commit.assert_called_once()
    mock_conn.close.assert_called_once()
