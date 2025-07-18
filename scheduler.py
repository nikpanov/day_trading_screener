
import time
import logging
from datetime import datetime
import pytz
from run_full_scan import run_full_scan
from config.settings import WATCHLIST_SCAN_LIMIT, COOLDOWN_SECONDS, TIGHTEN
from watchlist_scan import run_watchlist_scan
from db.writer import cleanup_screener_cache, cleanup_premarket_cache, cleanup_quote_cache


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

    full_scan_done = None
    final_scan_done = None
    last_watchlist_scan = None
    lunch_mode = False

    while True:
        now = now_et()
        current_time = now.time()

        try:
            if should_run_once(full_scan_done, datetime.strptime("09:30", "%H:%M").time(), datetime.strptime("10:30", "%H:%M").time()):
                logger.info("Running full scan (morning)")
                run_full_scan()

                # ✅ Cleanup old screener_cache entries                
                cleanup_screener_cache(days=14)
                cleanup_premarket_cache()
                cleanup_quote_cache(days=30)

                full_scan_done = now

            elif datetime.strptime("10:30", "%H:%M").time() <= current_time < datetime.strptime("12:00", "%H:%M").time():
                if should_run_every(last_watchlist_scan, 15):
                    logger.info("Running 15-min watchlist scan")                    
                    run_watchlist_scan(tighten=TIGHTEN)
                    last_watchlist_scan = now

            elif datetime.strptime("12:00", "%H:%M").time() <= current_time < datetime.strptime("13:30", "%H:%M").time():
                if not lunch_mode:
                    logger.info("Entering lunch mode — hourly scan")
                    lunch_mode = True
                if should_run_every(last_watchlist_scan, 60):
                    logger.info("🍵 Running hourly watchlist scan")
                    run_watchlist_scan(tighten=TIGHTEN)
                    last_watchlist_scan = now

            elif datetime.strptime("13:30", "%H:%M").time() <= current_time < datetime.strptime("15:00", "%H:%M").time():
                if lunch_mode:
                    logger.info("Exiting lunch mode — resume 15-min scans")
                    lunch_mode = False
                if should_run_every(last_watchlist_scan, 15):
                    logger.info("Running 15-min watchlist scan")
                    run_watchlist_scan(tighten=TIGHTEN)
                    last_watchlist_scan = now

            elif should_run_once(final_scan_done, datetime.strptime("15:00", "%H:%M").time(), datetime.strptime("15:45", "%H:%M").time()):
                logger.info("Running final full scan (mode=final)")
                run_full_scan(mode="final")
                final_scan_done = now

        except Exception as e:
            logger.error(f"Error during scheduler loop: {e}")

        time.sleep(30) # Sleep to avoid busy-waiting

if __name__ == "__main__":
    scheduler_loop()
