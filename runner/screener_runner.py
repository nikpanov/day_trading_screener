from api.fmp_client import fetch_core_screener, fetch_technicals
from utils.filters import is_bullish
from db.writer import save_run_and_results
from utils.exporter import export_to_excel
from datetime import datetime

def run_screener(limit=50):
    run_timestamp = datetime.utcnow()
    print(f"📡 Screener run at {run_timestamp}")

    results = fetch_core_screener(limit)
    all_results = []

    for stock in results:
        symbol = stock["symbol"]
        name = stock.get("companyName", "")
        price = stock.get("price")

        print(f"\n🔍 {symbol} - {name}")
        indicators = fetch_technicals(symbol)

        if not indicators:
            print("⚠️ No technical data — skipping.")
            continue

        bullish = is_bullish(price, indicators)
        if bullish:
            print("✅ Bullish signal!")

        all_results.append({
            "symbol": symbol,
            "company_name": name,
            "price": price,
            **indicators,
            "is_bullish": bullish,
            "timestamp": run_timestamp
        })

    save_run_and_results(all_results, run_timestamp)
    export_to_excel(all_results, run_timestamp)
