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
        logger.info("No bullish tickers to update in watchlist cache.")
        return

    symbols_today = set()
    rows = []

    for r in bullish_results:
        if r.get("symbol") and r.get("price") is not None and r.get("timestamp"):
            symbol = r["symbol"]
            symbols_today.add(symbol)
            rows.append((
                symbol,
                r["company_name"],
                r["price"],
                r["timestamp"],  # timestamp = detection time
                r["timestamp"],  # first_seen = same for new records
            ))

    insert_query = """
        INSERT INTO day_trading_screener.watchlist_cache (
            symbol, company_name, price, timestamp, first_seen
        )
        VALUES %s
        ON CONFLICT (symbol) DO UPDATE
        SET
            company_name = EXCLUDED.company_name,
            price = EXCLUDED.price,
            timestamp = EXCLUDED.timestamp,
            updated_at = NOW()
        WHERE EXCLUDED.timestamp > day_trading_screener.watchlist_cache.timestamp;
    """

    delete_query = """
        DELETE FROM day_trading_screener.watchlist_cache
        WHERE symbol NOT IN %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            # ✅ Upsert today's bullish tickers
            execute_values(cur, insert_query, rows)

            # ❌ Delete any tickers no longer bullish
            cur.execute(delete_query, (tuple(symbols_today),))

    logger.info(f"Watchlist cache updated: {len(rows)} bullish tickers kept or added. Others removed.")


