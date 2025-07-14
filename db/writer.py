from db import get_connection
from utils.logger import setup_logger
from psycopg2.extras import execute_values

logger = setup_logger()

def save_run_and_results(rows, run_timestamp): 
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO day_trading_screener.screener_run (run_timestamp) VALUES (%s) RETURNING run_id",
                    (run_timestamp,)
                )
                run_id = cur.fetchone()[0]

                values = [
                    (
                        run_id,
                        row["symbol"],
                        row["company_name"],
                        row["price"],
                        row["price"] > row["vwap"] if row["vwap"] else None,
                        row["ema20"] > row["ema50"] if row["ema20"] and row["ema50"] else None,
                        50 <= row["rsi14"] <= 70 if row["rsi14"] else None,
                        1.0 if row["is_bullish"] else 0.0,
                        row["timestamp"]
                    )
                    for row in rows
                ]

                execute_values(cur, """
                    INSERT INTO day_trading_screener.stock_result (
                        run_id, ticker, company_name, price,
                        passed_vwap, passed_ema, passed_rsi,
                        signal_strength, created_at
                    ) VALUES %s
                """, values)
    finally:
        conn.close()
        logger.info(f"Saved {len(rows)} results for run {run_id} at {run_timestamp}")

def update_watchlist_cache(bullish_results: list):
    if not bullish_results:
        return

    rows = [
        (
            r["symbol"],
            r["company_name"],
            r["price"],
            r["timestamp"]
        )
        for r in bullish_results
    ]

    query = """
        INSERT INTO day_trading_screener.watchlist_cache (symbol, company_name, price, timestamp, updated_at)
        VALUES %s
        ON CONFLICT (symbol) DO UPDATE SET
            company_name = EXCLUDED.company_name,
            price = EXCLUDED.price,
            timestamp = EXCLUDED.timestamp,
            updated_at = NOW();
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(cur, query, rows)