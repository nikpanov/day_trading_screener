
import time
import logging
from datetime import datetime, timedelta
from runner.screener_runner import run_screener
from db.reader import load_watchlist_symbols
import pytz

ET = pytz.timezone("US/Eastern")
logger = logging.getLogger("scheduler")
handler = logging.FileHandler("logs/scheduler.log", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def now_et():
    return datetime.now(ET)

def should_run_once(last_run, window_start, window_end):
    now = now_et()
    return window_start <= now.time() <= window_end and (last_run is None or last_run.date() != now.date())

def should_run_every(last_run, interval_min):
    if last_run is None:
        return True
    return (now_et() - last_run).total_seconds() >= interval_min * 60

def scheduler_loop():
    logger.info("📅 Scheduler started.")
    full_scan_done = None
    final_scan_done = None
    last_watchlist_scan = None
    lunch_mode = False

    while True:
        now = now_et()
        current_time = now.time()

        try:
            # ⏰ Full scan at 09:30 once
            if should_run_once(full_scan_done, datetime.strptime("09:30", "%H:%M").time(), datetime.strptime("10:30", "%H:%M").time()):
                logger.info("Running full scan (morning)")
                run_screener(limit=2500, use_optional_filters=True)
                full_scan_done = now

            # ⏱️ Watchlist scan every 15 minutes between 10:30–12:00
            elif datetime.strptime("10:30", "%H:%M").time() <= current_time < datetime.strptime("12:00", "%H:%M").time():
                if should_run_every(last_watchlist_scan, 15):
                    logger.info("Running 15-min watchlist scan")
                    from watchlist_scan import run_watchlist_scan
                    run_watchlist_scan()
                    last_watchlist_scan = now

            # 💤 Lunch pause or slow scan from 12:00–13:30
            elif datetime.strptime("12:00", "%H:%M").time() <= current_time < datetime.strptime("13:30", "%H:%M").time():
                if not lunch_mode:
                    logger.info("Entering lunch mode — slow scan")
                    lunch_mode = True
                if should_run_every(last_watchlist_scan, 60):
                    logger.info("🍵 Running hourly watchlist scan")
                    from watchlist_scan import run_watchlist_scan
                    run_watchlist_scan()
                    last_watchlist_scan = now

            # 🔁 Resume 15-min scans after lunch
            elif datetime.strptime("13:30", "%H:%M").time() <= current_time < datetime.strptime("15:00", "%H:%M").time():
                if lunch_mode:
                    logger.info("Exiting lunch mode — resume 15-min scans")
                    lunch_mode = False
                if should_run_every(last_watchlist_scan, 15):
                    logger.info("Running 15-min watchlist scan")
                    from watchlist_scan import run_watchlist_scan
                    run_watchlist_scan()
                    last_watchlist_scan = now

            # 🔁 Optional final full scan at 15:00–15:45
            elif should_run_once(final_scan_done, datetime.strptime("15:00", "%H:%M").time(), datetime.strptime("15:45", "%H:%M").time()):
                logger.info("Running final full scan")
                run_screener(limit=500, use_optional_filters=True)
                final_scan_done = now

        except Exception as e:
            logger.error(f"Error during scheduler loop: {e}")

        time.sleep(30)

if __name__ == "__main__":
    scheduler_loop()
