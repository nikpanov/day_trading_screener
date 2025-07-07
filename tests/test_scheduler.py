from scheduler.timing import is_market_open

def test_is_market_open_weekday_morning():
    import datetime
    dt = datetime.datetime(2025, 7, 3, 10, 0)  # Thursday
    assert is_market_open(dt) is True
