from api.fmp_client import fetch_core_screener, fetch_technicals
from utils.filters import is_bullish
from db.writer import save_run_and_results
from utils.exporter import export_to_excel
from datetime import datetime
from utils.logger import setup_logger
import time

logger = setup_logger()


def run_screener(limit=50):
    from utils.logger import setup_logger
    logger = setup_logger()

    run_timestamp = datetime.utcnow()
    logger.info(f"Screener run started at {run_timestamp} (limit={limit})")

    start_time = time.time()
    results = fetch_core_screener(limit)
    all_results = []
    bullish_count = 0
    failed_count = 0

    for stock in results:
        symbol = stock["symbol"]
        name = stock.get("companyName", "")
        price = stock.get("price")

        logger.info(f"{symbol} - {name}")
        indicators = fetch_technicals(symbol)

        if not indicators:
            logger.warning(f"No technical data — skipping {symbol}")
            failed_count += 1
            continue

        bullish = is_bullish(price, indicators)
        if bullish:
            logger.info(f"Bullish signal for {symbol}!")
            bullish_count += 1

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

    elapsed = time.time() - start_time
    logger.info("Screener Summary")
    logger.info(f"Bullish matches: {bullish_count}")
    logger.info(f"Failed (no technical data): {failed_count}")
    logger.info(f"Run duration: {elapsed:.2f} seconds")


