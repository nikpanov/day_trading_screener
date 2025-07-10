import pandas as pd
from datetime import datetime, timedelta
from db import get_connection
from utils.logger import setup_logger
from api.fmp_client import fetch_historical_prices
from utils.exporter import export_backtest_results_to_excel
import argparse
from collections import Counter

logger = setup_logger("backtester")

def simulate_trade(prices, buy_price, target_pct, stop_loss_pct):
    for i, row in prices.iterrows():
        change = (row['close'] - buy_price) / buy_price
        if change >= target_pct:
            return row['close'], row['date'], change, (row['date'] - prices.iloc[0]['date']).days, 'win'
        if change <= stop_loss_pct:
            return row['close'], row['date'], change, (row['date'] - prices.iloc[0]['date']).days, 'loss'

    last = prices.iloc[-1]
    change = (last['close'] - buy_price) / buy_price
    return last['close'], last['date'], change, (last['date'] - prices.iloc[0]['date']).days, 'neutral'

def run_backtest(hold_days=10, target_pct=0.05, stop_loss_pct=-0.03, history_days=None):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT symbol, company_name, timestamp::date AS signal_date, price AS buy_price
        FROM day_trading_screener.screener_cache
        WHERE is_bullish = true
    """
    if history_days:
        query += f" AND timestamp >= CURRENT_DATE - INTERVAL '{history_days} days'"
    query += " ORDER BY timestamp"

    cur.execute(query)
    rows = cur.fetchall()

    logger.info(f"Running backtest on {len(rows)} signals")
    results = []

    for symbol, company_name, signal_date, buy_price in rows:
        prices = fetch_historical_prices(symbol, start_date=signal_date + timedelta(days=1), days=hold_days)
        if prices is None or prices.empty:
            logger.warning(f"No historical data for {symbol} from {signal_date}")
            continue

        sell_price, sell_date, gain_pct, hold_days_actual, result = simulate_trade(
            prices, buy_price, target_pct, stop_loss_pct
        )

        results.append((
            symbol, signal_date, buy_price, sell_price,
            sell_date, gain_pct, hold_days_actual, result, company_name
        ))

    for row in results:
        cur.execute("""
            INSERT INTO day_trading_screener.backtest_results (
                symbol, signal_date, buy_price, sell_price,
                sell_date, gain_pct, holding_days, result, company_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, row)

    conn.commit()
    conn.close()
    logger.info(f"Backtest complete. Inserted {len(results)} results.")

    summary = Counter(r[7] for r in results)
    logger.info(f"Result summary: {dict(summary)}")

    export_backtest_results_to_excel(results, datetime.now())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run backtest simulation on bullish signals")
    parser.add_argument("--hold_days", type=int, default=10, help="Number of holding days after signal (default: 10)")
    parser.add_argument("--target", type=float, default=0.05, help="Target gain percentage (default: 0.05 = 5%)")
    parser.add_argument("--stop", type=float, default=-0.03, help="Stop loss percentage (default: -0.03 = -3%)")
    parser.add_argument("--history", type=int, help="Limit signals to the last N days")

    args = parser.parse_args()

    run_backtest(
        hold_days=args.hold_days,
        target_pct=args.target,
        stop_loss_pct=args.stop,
        history_days=args.history
    )


# how to run
# python backtester.py --hold_days 7 --target 0.04 --stop -0.02 --history 30
# target - profit percentage to exit trade
# stop - loss percentage to exit trade
# history - limit signals to the last N days (optional)

