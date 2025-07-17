import argparse
from runner.screener_runner import run_screener
from db.reader import load_watchlist_symbols
import logging
from utils.logger import setup_logger

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--tighten", action="store_true")
    parser.add_argument("--cooldown", type=int, default=30, help="Seconds to wait between batches")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logger(level=log_level)

    watchlist = load_watchlist_symbols()
    if not watchlist:
        logger.warning("Watchlist is empty. Nothing to scan.")
        return

    print(f"Watchlist scan: {len(watchlist)} symbols")

    run_screener(
        limit=len(watchlist),
        use_optional_filters=args.tighten,
        log_level=log_level,
        cooldown=args.cooldown,
        watchlist_symbols=watchlist
    )

if __name__ == "__main__":
    main()
