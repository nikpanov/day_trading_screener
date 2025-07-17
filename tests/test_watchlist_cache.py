from db.writer import update_watchlist_cache
from datetime import datetime, timezone

# Simulated bullish results from today's scan
today = datetime.now(timezone.utc)

fake_today_results = [
    {
        "symbol": "AAPL",
        "company_name": "Apple Inc.",
        "price": 210.0,
        "timestamp": today
    },
    {
        "symbol": "MSFT",
        "company_name": "Microsoft Corp.",
        "price": 310.5,
        "timestamp": today
    }
]

update_watchlist_cache(fake_today_results)
print("✅ Watchlist cache update test complete.")
