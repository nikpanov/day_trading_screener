import pytest
from unittest.mock import patch
from data.fetchers import fetch_fundamentals

@patch("data.fetchers.requests.get")
def test_fetch_fundamentals_mocked(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "symbol": "AAPL",
        "beta": 1.25,
        "market_cap": 950000000
    }

    result = fetch_fundamentals("AAPL")
    assert result["beta"] == 1.25
    assert "market_cap" in result
