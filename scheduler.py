# scheduler.py
import argparse
import time
from datetime import datetime, timezone
from runner.screener_runner import run_screener
from utils.logger import setup_logger
from logging.handlers import RotatingFileHandler
import logging
from datetime import datetime, time as dt_time
import pytz

def is_market_open():
    now = datetime.now(pytz.timezone("US/Eastern")).time()
    return dt_time(9, 30) <= now <= dt_time(16, 0)

def get_dynamic_interval():
    now = datetime.now(pytz.timezone("US/Eastern")).time()

    # Market open-close window
    if dt_time(9, 30) <= now < dt_time(10, 0):     # First 30 min after open
        return 15
    elif dt_time(10, 0) <= now < dt_time(15, 30):  # Midday
        return 30
    elif dt_time(15, 30) <= now <= dt_time(16, 0): # Last 30 min before close
        return 15
    else:
        return None

def schedule_runner(limit, tighten, interval_minutes):
    logger = logging.getLogger("screener")

    logger.info(f"Scheduler started. Running every {interval_minutes} minutes.")
    try:
        while True:
            if is_market_open():
                run_timestamp = datetime.now(timezone.utc)
                logger.info(f"Triggering run_screener() at {run_timestamp}")
                interval = get_dynamic_interval()
                if interval is None:
                    logger.info("Market closed. Sleeping for 5 minutes...")
                    time.sleep(300)
                    continue
                logger.info(f"Triggering run_screener() at {datetime.utcnow()}")
                try:
                    run_screener(limit=limit, use_optional_filters=tighten)
                except Exception as e:
                    logger.error(f"Error during run: {e}")
                logger.info(f"Sleeping for {interval_minutes} minutes...\n")
                time.sleep(interval_minutes * 60)
            else:
                logger.info("Market is closed. Sleeping 5 minutes...")
                time.sleep(300)
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
