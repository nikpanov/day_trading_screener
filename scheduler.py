# scheduler.py
import argparse
import time
from datetime import datetime, timezone
from runner.screener_runner import run_screener
from utils.logger import setup_logger
from logging.handlers import RotatingFileHandler
import logging

def schedule_runner(limit, tighten, interval_minutes):
    logger = logging.getLogger("screener")

    logger.info(f"Scheduler started. Running every {interval_minutes} minutes.")
    try:
        while True:
            run_timestamp = datetime.now(timezone.utc)
            logger.info(f"Triggering run_screener() at {run_timestamp}")
            try:
                run_screener(limit=limit, use_optional_filters=tighten)
            except Exception as e:
                logger.error(f"Error during run: {e}")
            logger.info(f"Sleeping for {interval_minutes} minutes...\n")
            time.sleep(interval_minutes * 60)
    except KeyboardInterrupt:
        logger.info("Scheduler interrupted by user. Shutting down cleanly.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--tighten", action="store_true")
    parser.add_argument("--interval", type=int, default=15, help="Minutes between screener runs")
    args = parser.parse_args()

    # Setup rotating logger
    log_level = logging.DEBUG if args.debug else logging.INFO
    logger = setup_logger(level=log_level)
    logger.handlers = []  # Clear existing

    # File handler with rotation
    file_handler = RotatingFileHandler("logs/app.log", maxBytes=5_000_000, backupCount=5)
    file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    file_handler.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))
    console_handler.setLevel(log_level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    schedule_runner(limit=args.limit, tighten=args.tighten, interval_minutes=args.interval)

if __name__ == "__main__":
    main()
