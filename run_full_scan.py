# run_full_scan.py
from runner.screener_runner import run_screener
from db.writer import update_watchlist_cache
from db.reader import get_last_run_id, fetch_screener_results
import logging
from config.settings import FULL_SCAN_LIMIT

logger = logging.getLogger("full_scan")

def run_full_scan():
    run_screener(limit=FULL_SCAN_LIMIT, use_optional_filters=True)

    run_id = get_last_run_id()
    results = fetch_screener_results(run_id)

    logger.info(f"Fetched {len(results)} results from run {run_id}")
    update_watchlist_cache(results)
    logger.info(f"Watchlist cache updated with bullish tickers.")

if __name__ == "__main__":
    run_full_scan()

# This script is intended to be run as a standalone process to perform a full scan
# and update the watchlist cache with the latest bullish tickers.
# It can be scheduled to run periodically or triggered manually as needed.
# Ensure that the database connection and other dependencies are properly configured.
# Logging is set up to capture the process flow and any issues that arise.
# Adjust the logging level as needed for debugging or production use.
# The run_screener function is called with a limit of 2500 to ensure a comprehensive scan.
# The use_optional_filters flag is set to True to apply additional filters during the scan.
# After the scan, the results are fetched and the watchlist cache is updated accordingly.
# This script can be integrated into a larger scheduling system or run independently.
# Make sure to handle any exceptions or errors that may occur during the process.
# The logger will provide detailed information about the scan process and results.
# Consider adding more error handling and logging as needed for production use.