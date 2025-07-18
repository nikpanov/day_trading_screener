# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

DB_SETTINGS = {
    "host": os.getenv("PG_HOST"),
    "port": os.getenv("PG_PORT"),
    "database": os.getenv("PG_DB"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
}

FMP_API_KEY = os.getenv("FMP_API_KEY")

# Batch execution for FMP Starter plan to eliminate 429 errors
BATCH_SIZE = 30  
COOLDOWN_SECONDS  = 30  


# Scan limits
FULL_SCAN_LIMIT = 2500         # 🧠 Morning and final full scans
WATCHLIST_SCAN_LIMIT = 500     # ⏱️ Watchlist scans throughout the day
DEBUG_SCAN_LIMIT = 50          # 🐞 For manual tests and dev runs

#
TIGHTEN=True  # 🛠️ Use optional filters in scans