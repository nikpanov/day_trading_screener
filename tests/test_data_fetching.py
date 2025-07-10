import pytest
from unittest.mock import patch
from api.fmp_client import fetch_fundamentals

@patch("api.fmp_client.requests.get")
def test_fetch_fundamentals_mocked(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{
        "symbol": "AAPL",
        "beta": 1.25,
        "mktCap": 950000000
    }]

    result = fetch_fundamentals("AAPL")
    assert result["beta"] == 1.25
    assert "market_cap" in result
