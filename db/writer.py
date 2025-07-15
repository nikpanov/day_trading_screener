from db import get_connection
from utils.logger import setup_logger
from psycopg2.extras import execute_values
from datetime import datetime

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
                        # SAFE: price > vwap only if both are not None
                        row["price"] > row["vwap"] if row["price"] is not None and row["vwap"] is not None else None,
                        # SAFE: ema20 > ema50 only if both exist
                        row["ema20"] > row["ema50"] if row.get("ema20") is not None and row.get("ema50") is not None else None,
                        # SAFE: RSI in 50-70 range only if rsi14 exists
                        50 <= row["rsi14"] <= 70 if row.get("rsi14") is not None else None,
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
            r["timestamp"],   # timestamp is when scan ran
            r["timestamp"]    # first_seen will be same initially
        )
        for r in bullish_results
    ]

    query = """
        INSERT INTO day_trading_screener.watchlist_cache (symbol, company_name, price, timestamp, first_seen, updated_at)
        VALUES %s
        ON CONFLICT (symbol) DO UPDATE
        SET
            company_name = EXCLUDED.company_name,
            price = EXCLUDED.price,
            timestamp = EXCLUDED.timestamp,
            updated_at = NOW()
        WHERE EXCLUDED.timestamp > watchlist_cache.timestamp;
    """

    delete_old_query = """
        DELETE FROM watchlist_cache
        WHERE DATE(timestamp) < CURRENT_DATE;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Optional: clear stale records first
            cur.execute(delete_old_query)
            execute_values(cur, query, rows)