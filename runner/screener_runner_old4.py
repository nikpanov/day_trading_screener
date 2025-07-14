import logging
import time
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from api.fmp_client import fetch_core_screener, fetch_technicals, fetch_fundamentals, fetch_pre_market_change
from utils.filters import is_bullish
from db.writer import save_run_and_results
from utils.exporter import export_screener_results_to_excel
from utils.logger import setup_logger
from db.cache import upsert_screener_cache, upsert_premarket_cache
from pytz import timezone as pytz_timezone

ET = pytz_timezone("US/Eastern")

def now_et():
    return datetime.now(ET)

def run_screener(limit=50, use_optional_filters=False, log_level=logging.INFO, cooldown=3):
    def chunkify(lst, batch_size):
        for i in range(0, len(lst), batch_size):
            yield lst[i:i + batch_size]

    logger = setup_logger(level=log_level)
    run_timestamp = datetime.now(timezone.utc)
    logger.info(f"Screener run started at {run_timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')} (limit={limit})")

    start_time = time.time()
    results = fetch_core_screener(limit)
    all_results = []
    bullish_count = 0
    failed_count = 0

    def analyze_stock(stock):
        symbol = stock["symbol"]
        name = stock.get("companyName", "")
        price = stock.get("price")
        logger.info(f"{symbol} - {name}")

        indicators = fetch_technicals(symbol)
        fundamentals = fetch_fundamentals(symbol) if use_optional_filters else None
        pre_market_change_pct = fetch_pre_market_change(symbol) if use_optional_filters else None

        if not indicators:
            logger.warning(f"No technical data — skipping {symbol}")
            result = {
            "symbol": symbol,
            "company_name": name,
            "price": price,
            "is_bullish": False,
            "timestamp": run_timestamp,
            "failure_reason": "No technical data"
            }

            return {"failed": False, "bullish": False, "result": result}

        reasons = []
        is_bullish_flag = is_bullish(
            price,
            indicators,
            fundamentals,
            pre_market_change_pct,
            use_optional_filters,
            logger,
            symbol,
            reasons
        )

        if is_bullish_flag:
            logger.info(f"Bullish signal for {symbol}!")
        else:
            for reason in reasons:
                logger.debug(f"{symbol}: {reason}")

        result = {
            "symbol": symbol,
            "company_name": name,
            "price": price,
            **indicators,
            "is_bullish": is_bullish_flag,
            "timestamp": run_timestamp,
            "failure_reason": "; ".join(reasons) if reasons else ""
        }

        upsert_screener_cache(result)
        if use_optional_filters and pre_market_change_pct is not None:
            upsert_premarket_cache(symbol, pre_market_change_pct)

        return {"failed": False, "bullish": is_bullish_flag, "result": result}

    batch_size = 30
    batches = list(chunkify(results, batch_size))

    with ThreadPoolExecutor(max_workers=8) as executor:
        for i, batch in enumerate(batches, start=1):
            logger.info(f"Processing batch {i} with {len(batch)} stocks...")
            futures = [executor.submit(analyze_stock, stock) for stock in batch]

            for future in as_completed(futures):
                data = future.result()
                if data["failed"]:
                    failed_count += 1
                    continue

                result = data["result"]
                all_results.append(result)
                if data["bullish"]:
                    bullish_count += 1

            if i < len(batches):
                logger.debug(f"Sleeping {cooldown} seconds before next batch...")
                time.sleep(cooldown)

    save_run_and_results(all_results, run_timestamp)
    export_screener_results_to_excel(all_results, run_timestamp)

    elapsed = time.time() - start_time
    logger.info("Screener Summary")
    logger.info(f"Bullish matches: {bullish_count}")
    logger.info(f"Failed (no technical data): {failed_count}")
    logger.info(f"Run duration: {elapsed:.2f} seconds")
