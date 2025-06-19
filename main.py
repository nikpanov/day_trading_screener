import argparse
import logging
from runner.screener_runner import run_screener
from utils.logger import setup_logger

def main():
    parser = argparse.ArgumentParser(description="Run the day trading screener.")
    parser.add_argument("--debug", action="store_true", help="Enable debug-level logging")
    parser.add_argument("--limit", type=int, default=50, help="Number of tickers to fetch from screener")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logger(level=log_level)

    run_screener(limit=args.limit)

if __name__ == "__main__":
    main()
