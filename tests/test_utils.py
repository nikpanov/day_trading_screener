# import pytest
# from utils.filters import is_bullish

# def test_is_bullish_all_positive():
#     metrics = {
#         "Price Action": 1,
#         "Moving Averages": 1,
#         "Volume Analysis": 1,
#         "MACD_RSI": 1,
#         "Fundamentals": 1,
#     }
#     assert is_bullish(metrics) is True

# @pytest.mark.parametrize("metrics,expected", [
#     ({"Price Action": 1, "Moving Averages": 0, "Volume Analysis": 1, "MACD_RSI": 1, "Fundamentals": 1}, False),
#     ({"Price Action": 1, "Moving Averages": 1, "Volume Analysis": 0, "MACD_RSI": 1, "Fundamentals": 1}, False),
#     ({"Price Action": 1, "Moving Averages": 1, "Volume Analysis": 1, "MACD_RSI": 1, "Fundamentals": 1}, True),
# ])

# def test_is_bullish_parametrized(metrics, expected):
#     assert is_bullish(metrics) == expected

# #2
import pytest
from utils.filters import is_bullish, apply_optional_filters


@pytest.mark.parametrize("metrics,expected", [
    ({"Price Action": 1, "Moving Averages": 1, "Volume Analysis": 1, "MACD_RSI": 1, "Fundamentals": 1}, True),
    ({"Price Action": 1, "Moving Averages": 0, "Volume Analysis": 1, "MACD_RSI": 1, "Fundamentals": 1}, False),
    ({"Price Action": 0, "Moving Averages": 1, "Volume Analysis": 1, "MACD_RSI": 1, "Fundamentals": 1}, False),
])
def test_is_bullish(metrics, expected):
    assert is_bullish(metrics) == expected


@pytest.mark.parametrize("fundamentals, premarket, expected", [
    ({"beta": 1.1, "market_cap": 1_000_000_000}, 0.03, True),
    ({"beta": 1.9, "market_cap": 1_000_000_000}, 0.03, False),  # beta too high
    ({"beta": 1.1, "market_cap": 10_000_000}, 0.03, False),     # market cap too low
    ({"beta": 1.1, "market_cap": 1_000_000_000}, -0.10, False), # premarket too negative
])
def test_apply_optional_filters(fundamentals, premarket, expected):
    assert apply_optional_filters(fundamentals, premarket) == expected
