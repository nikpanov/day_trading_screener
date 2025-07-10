import pytest
from unittest.mock import patch, MagicMock
from db.writer import save_run_and_results
from datetime import datetime

@patch("db.writer.get_connection")
@patch("db.writer.execute_values")
def test_save_run_and_results(mock_execute_values, mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value.__enter__.return_value
    mock_get_conn.return_value = mock_conn
    mock_cursor.fetchone.return_value = [123]  # Simulate RETURNING run_id

    rows = [
        {
            "symbol": "AAPL",
            "company_name": "Apple Inc.",
            "price": 185.5,
            "vwap": 180.2,
            "ema20": 183.0,
            "ema50": 182.0,
            "rsi14": 60,
            "is_bullish": True,
            "timestamp": datetime(2025, 7, 7, 14, 0)
        }
    ]
    run_timestamp = datetime(2025, 7, 7, 14, 0)

    save_run_and_results(rows, run_timestamp)

    mock_cursor.execute.assert_called_once()
    sql = mock_cursor.execute.call_args[0][0]
    assert "INSERT INTO day_trading_screener.screener_run" in sql

    mock_execute_values.assert_called_once()
    args, kwargs = mock_execute_values.call_args
    assert "INSERT INTO day_trading_screener.stock_result" in args[1]
    assert len(args[2]) == 1  # One row
    assert args[2][0][1] == "AAPL"

    mock_conn.close.assert_called_once()
