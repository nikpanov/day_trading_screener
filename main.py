import argparse
import logging
from runner.screener_runner import run_screener
from utils.logger import setup_logger


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--tighten", action="store_true", help="Apply optional filters: beta > 1, market cap >= 2B, pre-market change > 1%")
    args = parser.parse_args()

    # Set log level based on --debug
    log_level = logging.DEBUG if args.debug else logging.INFO
  
    run_screener(limit=args.limit, use_optional_filters=args.tighten, log_level=log_level)

if __name__ == "__main__":
    main()
