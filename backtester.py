import os
import pandas as pd
from datetime import datetime, timedelta
from db import get_connection
from utils.logger import setup_logger
from api.fmp_client import fetch_historical_prices
from openpyxl.styles import PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import Workbook

logger = setup_logger("backtester")

HOLD_DAYS = 10
TARGET_PCT = 0.05
STOP_LOSS_PCT = -0.03

def simulate_trade(prices, buy_price):
    for i, row in prices.iterrows():
        change = (row['close'] - buy_price) / buy_price
        if change >= TARGET_PCT:
            return row['close'], row['date'], change, (row['date'] - prices.iloc[0]['date']).days, 'win'
        if change <= STOP_LOSS_PCT:
            return row['close'], row['date'], change, (row['date'] - prices.iloc[0]['date']).days, 'loss'

    last = prices.iloc[-1]
    change = (last['close'] - buy_price) / buy_price
    return last['close'], last['date'], change, (last['date'] - prices.iloc[0]['date']).days, 'neutral'

def run_backtest():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT symbol, timestamp::date AS signal_date, price AS buy_price
        FROM day_trading_screener.screener_cache
        WHERE is_bullish = true
        ORDER BY timestamp
    """)
    rows = cur.fetchall()

    logger.info(f"Running backtest on {len(rows)} signals")
    results = []

    for symbol, signal_date, buy_price in rows:
        prices = fetch_historical_prices(symbol, start_date=signal_date + timedelta(days=1), days=HOLD_DAYS)
        if prices is None or prices.empty:
            logger.warning(f"No historical data for {symbol} from {signal_date}")
            continue

        sell_price, sell_date, gain_pct, hold_days, result = simulate_trade(prices, buy_price)

        results.append((symbol, signal_date, buy_price, sell_price, sell_date, gain_pct, hold_days, result))

    for row in results:
        cur.execute("""
            INSERT INTO day_trading_screener.backtest_results (symbol, signal_date, buy_price, sell_price, sell_date, gain_pct, holding_days, result)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, row)

    conn.commit()
    conn.close()
    logger.info(f"Backtest complete. Inserted {len(results)} results.")

    # Export to Excel
    export_to_excel(results)

def export_to_excel(results):
    os.makedirs("output", exist_ok=True)
    df = pd.DataFrame(results, columns=[
        "symbol", "signal_date", "buy_price", "sell_price", "sell_date", "gain_pct", "holding_days", "result"
    ])
    filename = f"output/backtest_results_{datetime.now().strftime('%Y-%m-%d_%H%M')}.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Backtest Results"

    for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), start=1):
        ws.append(row)

        if r_idx == 1:
            # Bold header row
            for cell in ws[r_idx]:
                cell.font = cell.font.copy(bold=True)
            continue

        result = df.loc[r_idx - 2, "result"]
        if result == "win":
            fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        elif result == "loss":
            fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
        else:
            fill = None

        if fill:
            for cell in ws[r_idx]:
                cell.fill = fill

    wb.save(filename)
    print(f"\U0001f4e4 Exported backtest results to Excel: {filename}")

if __name__ == "__main__":
    run_backtest()
