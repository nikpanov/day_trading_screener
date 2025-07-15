from db import get_connection

def load_watchlist_symbols():
    query = """
        SELECT symbol FROM day_trading_screener.watchlist_cache
        ORDER BY updated_at DESC;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return [row[0] for row in cur.fetchall()]
