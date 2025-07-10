import pytest
from unittest.mock import patch, MagicMock
from db.ticker_rotation_import_fmp import import_tickers_from_fmp

@patch("db.ticker_rotation_import_fmp.get_connection")
@patch("db.ticker_rotation_import_fmp.fetch_core_screener")
def test_import_tickers_from_fmp(mock_fetch_core, mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = mock_conn.cursor.return_value
    mock_get_conn.return_value = mock_conn

    # Mock fetch_core_screener to return sample tickers
    mock_fetch_core.return_value = [
        {"symbol": "AAPL"},
        {"symbol": "MSFT"},
        {"symbol": "GOOG"},
        {"symbol": ""},
        {},
    ]

    # Simulate all INSERTs succeeding (rowcount > 0)
    mock_cursor.rowcount = 1

    import_tickers_from_fmp(limit=5)

    # 3 valid symbols should be inserted
    assert mock_cursor.execute.call_count == 3
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
