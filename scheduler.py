
import time
import logging
from datetime import datetime, time as dtime
import pytz
from runner.screener_runner import run_screener
from watchlist_scan import run_watchlist_scan
from db.reader import get_last_run_time
from emailer.notify import send_email_notification

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
    logger.info("Scheduler started.")
    logger.info("Schedule summary: 09:30 full scan, 10:30–15:00 15-min scans, 12:00–13:30 hourly lunch mode, 15:00 final scan")

    last_known_run = get_last_run_time()

    full_scan_done = None
    final_scan_done = None
    last_watchlist_scan = None
    lunch_mode = False

    while True:
        now = now_et()
        current_time = now.time()

        # ✅ Check for missed runs
        if last_known_run and (now - last_known_run).total_seconds() > 60 * 60:
            msg = f"No screener run recorded in the last hour.\nLast run: {last_known_run.strftime('%Y-%m-%d %H:%M:%S')}"
            logger.warning(msg)
            try:
                send_email_notification(subject="Screener Inactive Warning", body=msg)
            except Exception as e:
                logger.error(f"Failed to send inactivity alert: {e}")

        try:
            if should_run_once(full_scan_done, dtime(9, 30), dtime(10, 30)):
                logger.info("Running full scan (morning)")
                run_screener(limit=2500, use_optional_filters=True)
                last_known_run = now_et()
                full_scan_done = now_et()

            elif dtime(10, 30) <= current_time < dtime(12, 0):
                if should_run_every(last_watchlist_scan, 15):
                    logger.info("Running 15-min watchlist scan")
                    run_watchlist_scan(tighten=True, cooldown=30)
                    last_known_run = now_et()
                    last_watchlist_scan = now_et()

            elif dtime(12, 0) <= current_time < dtime(13, 30):
                if not lunch_mode:
                    logger.info("Entering lunch mode — slow scan")
                    lunch_mode = True
                if should_run_every(last_watchlist_scan, 60):
                    logger.info("Running hourly watchlist scan")
                    run_watchlist_scan(tighten=True, cooldown=30)
                    last_known_run = now_et()
                    last_watchlist_scan = now_et()

            elif dtime(13, 30) <= current_time < dtime(15, 0):
                if lunch_mode:
                    logger.info("Exiting lunch mode — resume 15-min scans")
                    lunch_mode = False
                if should_run_every(last_watchlist_scan, 15):
                    logger.info("Running 15-min watchlist scan")
                    run_watchlist_scan(tighten=True, cooldown=30)
                    last_known_run = now_et()
                    last_watchlist_scan = now_et()

            elif should_run_once(final_scan_done, dtime(15, 0), dtime(15, 45)):
                logger.info("Running final full scan (mode=final)")
                run_screener(limit=500, use_optional_filters=True, mode="final")
                last_known_run = now_et()
                final_scan_done = now_et()

        except Exception as e:
            logger.error(f"Error during scheduler loop: {e}")

        time.sleep(30)

if __name__ == "__main__":
    scheduler_loop()
