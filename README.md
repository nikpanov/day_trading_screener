
# Day Trading Screener

A modular Python application for identifying bullish trading signals using real-time stock data and technical indicators. This tool supports full market scans, watchlist-based scans, and automated scheduling for intra-day screening.

## 🔧 Features

- Fetches real-time stock data from Financial Modeling Prep API
- Detects bullish trends based on:
  - RSI, EMA, VWAP, volume, price action, and pre-market movement
- Automatically stores results in PostgreSQL (`screener_run`, `stock_result`, `watchlist_cache`)
- Schedules scans based on trading hours using `scheduler.py`
- Highlights results in Excel and sends summary emails

## 🚀 Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file with:

```
FMP_API_KEY=your_api_key_here
EMAIL_SENDER=sender@example.com
EMAIL_RECEIVER=receiver@example.com
EMAIL_PASSWORD=your_password
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_pass
DB_HOST=localhost
DB_PORT=5432
```

### 3. Run Manually

**Full scan:**

```bash
python run_full_scan.py
```

**Watchlist scan:**

```bash
python watchlist_scan.py --tighten
```

## ⏰ Automated Scanning

Use Task Scheduler or cron to run:

```bash
python scheduler.py
```

It performs:
- Full scan at 09:30
- 15-min scans 10:30–12:00 and 13:30–15:00
- Hourly lunch scan 12:00–13:30

## 📁 Project Structure

```
day_trading_screener/
├── api/                   # FMP API clients
├── db/                    # DB readers/writers and caching
├── runner/                # Screener execution logic
├── utils/                 # Filters, logger, emailer
├── output/                # Generated Excel files
├── scheduler.py           # Orchestrates scan schedule
├── run_full_scan.py       # Full scan + cache update
├── watchlist_scan.py      # Re-scans only watchlist tickers
├── requirements.txt
```

## 📊 Output

- Excel files saved under `output/screener_results/`
- Summary emails sent with results and top bullish tickers
- PostgreSQL DB stores detailed historical signals

## ✅ Status

Production-ready for scheduled screening and email alerts.
