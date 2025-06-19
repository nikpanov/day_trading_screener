# Day Trading Screener

A day trading stock screener using real-time market data and PostgreSQL.

## Features
- Core and technical filters for intraday momentum
- PostgreSQL schema for screener runs, results, technicals, and caching
- Output to XLSX for inspection or reporting
- Modular and testable with pytest

## Setup
1. Create `.env` file based on `.env.example`
2. Create a virtual environment:
python -m venv .venv
.venv/Scripts/activate 
pip install -r requirements.txt
3. Run the schema setup

4. Run tests

## Main functionality
main.py
│
├── fetch_core_screener()      → from FMP (volume, rel vol, % change, etc.)
├── enrich_technicals()        → VWAP, EMA, RSI
├── apply_filters()            → VWAP > price, 20 EMA > 50 EMA, RSI ∈ (50, 70)
├── write_to_db()              → Save to PostgreSQL
└── export_to_excel()          → Save to output/
