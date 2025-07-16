import time
import logging
import schedule
import subprocess
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger("scheduler")

def run_task(command):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Starting task: {command} at {timestamp}")
    try:
        subprocess.run(command, shell=True, check=True)
        logger.info(f"Completed task: {command}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed task: {command} — {e}")

# 1. Full scan at 09:30
schedule.every().day.at("09:30").do(run_task, "PYTHONPATH=. python full_scan.py --mode default --cooldown 30 --limit 3000")

# 2. Watchlist scan every 15 min until 12:00
for hour in range(9, 12):
    for minute in [0, 15, 30, 45]:
        schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(run_task, "PYTHONPATH=. python watchlist_scan.py --tighten --cooldown 30")

# 3. Reduced frequency (every hour) from 12:00 to 13:30
schedule.every().day.at("12:00").do(run_task, "PYTHONPATH=. python watchlist_scan.py --tighten --cooldown 30")
schedule.every().day.at("13:00").do(run_task, "PYTHONPATH=. python watchlist_scan.py --tighten --cooldown 30")

# 4. Final scan at 15:00
schedule.every().day.at("15:00").do(run_task, "PYTHONPATH=. python full_scan.py --mode final --cooldown 30 --limit 500")

# Keep the scheduler running
logger.info("Scheduler started. Waiting for tasks...")
while True:
    schedule.run_pending()
    time.sleep(1)
