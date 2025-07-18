import argparse
import logging
from runner.screener_runner import run_screener
from db.reader import load_watchlist_symbols
from utils.logger import setup_logger

def run_watchlist_scan(tighten=False, log_level=logging.INFO):
    logger = setup_logger(level=log_level)

    watchlist = load_watchlist_symbols()
    if not watchlist:
        logger.warning("Watchlist is empty. Nothing to scan.")
        return

    logger.info(f"Watchlist scan: {len(watchlist)} symbols")

    run_screener(
        limit=len(watchlist),
        use_optional_filters=tighten,
        log_level=log_level,        
        watchlist_symbols=watchlist
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--tighten", action="store_true")   
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    run_watchlist_scan(
        tighten=args.tighten,        
        log_level=log_level
    )

if __name__ == "__main__":
    main()
