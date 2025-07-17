from db import get_connection

def load_watchlist_symbols():
    query = """
        SELECT symbol
        FROM day_trading_screener.watchlist_cache
        ORDER BY updated_at DESC;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return [row[0] for row in cur.fetchall()]

def load_watchlist_metadata(symbol_list):
    if not symbol_list:
        return {}

    query = """
        SELECT symbol, company_name, price
        FROM day_trading_screener.watchlist_cache
        WHERE symbol = ANY(%s)
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (symbol_list,))
            rows = cur.fetchall()
            return {row[0]: {"company_name": row[1], "price": row[2]} for row in rows}

def get_last_run_id():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT run_id
                FROM day_trading_screener.screener_run
                ORDER BY run_timestamp DESC
                LIMIT 1
            """)
            row = cur.fetchone()
            return row[0] if row else None

def fetch_screener_results(run_id):
    query = """
        SELECT ticker, company_name, price, created_at
        FROM day_trading_screener.stock_result
        WHERE run_id = %s AND signal_strength = 1.0
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (run_id,))
            return [
                {
                    "symbol": row[0],
                    "company_name": row[1],
                    "price": float(row[2]) if row[2] is not None else None,
                    "timestamp": row[3],
                }
                for row in cur.fetchall()
            ]