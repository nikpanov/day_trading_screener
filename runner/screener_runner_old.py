
from api.fmp_client import fetch_core_screener, fetch_technicals, fetch_fundamentals, fetch_pre_market_change
from utils.filters import is_bullish
from db.writer import save_run_and_results
from utils.exporter import export_screener_results_to_excel
from utils.logger import setup_logger
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from db.cache import upsert_screener_cache, upsert_premarket_cache
import logging
from datetime import datetime, timezone
from pytz import timezone as pytz_timezone
import traceback

ET = pytz_timezone("US/Eastern")

def now_et():
    return datetime.now(ET)

logger = setup_logger()

def run_screener(limit=50, use_optional_filters=False, log_level=logging.INFO, cooldown=30, watchlist_symbols=None):
    def chunkify(lst, batch_size):
        for i in range(0, len(lst), batch_size):
            yield lst[i:i + batch_size]

    logger = setup_logger(level=log_level)
    run_timestamp = datetime.now(timezone.utc)
    logger.info(f"Screener run started at {run_timestamp.strftime('%Y-%m-%d %H:%M:%S %Z')} (limit={limit})")

    start_time = time.time()
    # results = fetch_core_screener(limit)
    # When called with watchlist_symbols, we skip the FMP screener and re-use previous tickers.
    # results = fetch_core_screener(limit) if watchlist_symbols is None else [{"symbol": s} for s in watchlist_symbols]
    if watchlist_symbols is None:
        results = fetch_core_screener(limit)
    else:
        # enrich with cached metadata (name and price)
        from db.reader import load_watchlist_metadata

        if isinstance(watchlist_symbols[0], dict):  # from watchlist scan
            symbols = [d["symbol"] for d in watchlist_symbols]
        else:
            symbols = watchlist_symbols

        symbol_metadata = load_watchlist_metadata(symbols)
        results = [
            {
                "symbol": symbol,
                "company_name": symbol_metadata.get(symbol, {}).get("company_name", ""),
                "price": symbol_metadata.get(symbol, {}).get("price", None)
            }
            for symbol in watchlist_symbols
        ]

    all_results = []
    bullish_count = 0
    failed_count = 0

    def analyze_stock(stock):
        symbol = stock["symbol"]
        name = stock.get("companyName", "")
        price = stock.get("price")
        logger.info(f"{symbol} - {name}")

        try:
            indicators = fetch_technicals(symbol)
            if not indicators:
                raise ValueError("No technical data")

            fundamentals = fetch_fundamentals(symbol) if use_optional_filters else None
            pre_market_change_pct = fetch_pre_market_change(symbol) if use_optional_filters else None

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

        except Exception as e:
            logger.warning(f"{symbol} - error: {e}")
            return {"failed": True}



    batch_size = 30    
    with ThreadPoolExecutor(max_workers=8) as executor:
        for i, batch in enumerate(chunkify(results, batch_size), start=1):
            logger.info(f"Processing batch {i} with {len(batch)} stocks...")
            futures = [executor.submit(analyze_stock, stock) for stock in batch]

            for future in as_completed(futures):
                try:
                    data = future.result()
                except Exception as e:
                    logger.warning(f"Unhandled error in future: {e}")
                    failed_count += 1
                    continue

                if data.get("failed"):
                    failed_count += 1
                    continue

                result = data["result"]
                all_results.append(result)
                if data.get("bullish"):
                    bullish_count += 1

            if i * batch_size < limit:
                logger.info(f"Cooldown for {cooldown} seconds before next batch...")
                time.sleep(cooldown)
    
    # Calculate bullish duration for each result
    for row in all_results:
        if row.get("first_seen"):
            row["bullish_duration"] = (datetime.now(timezone.utc) - row["first_seen"]).days
        else:
            row["bullish_duration"] = 0

    
    save_run_and_results(all_results, run_timestamp)
    export_screener_results_to_excel(all_results, run_timestamp)

    elapsed = time.time() - start_time
    logger.info("Screener Summary")
    logger.info(f"Bullish matches: {bullish_count}")
    logger.info(f"Failed (errors or missing data): {failed_count}")
    logger.info(f"Run duration: {elapsed:.2f} seconds")
