# run_full_scan_test.py
from runner.screener_runner import run_screener
from db.writer import  update_watchlist_cache
from db.reader import get_last_run_id, fetch_screener_results
import logging

logger = logging.getLogger("full_scan")

if __name__ == "__main__":

    run_screener(limit=2500, use_optional_filters=True)
    
    run_id = get_last_run_id()
    results = fetch_screener_results(run_id)
    
    logger.info(f"Fetched {len(results)} results from run {run_id}")

    update_watchlist_cache(results)
    logger.info(f"Watchlist cache updated with bullish tickers.")
