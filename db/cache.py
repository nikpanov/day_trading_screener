from db import get_connection
from utils.logger import setup_logger

logger = setup_logger()

def upsert_screener_cache(data):
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO day_trading_screener.screener_cache (
                    symbol, company_name, price, rsi14, ema20, ema50, vwap,
                    is_bullish, failure_reason, timestamp
                )
                VALUES (
                    %(symbol)s, %(company_name)s, %(price)s, %(rsi14)s, %(ema20)s,
                    %(ema50)s, %(vwap)s, %(is_bullish)s, %(failure_reason)s, %(timestamp)s
                )
                ON CONFLICT (symbol,timestamp) DO UPDATE SET
                    company_name = EXCLUDED.company_name,
                    price = EXCLUDED.price,
                    rsi14 = EXCLUDED.rsi14,
                    ema20 = EXCLUDED.ema20,
                    ema50 = EXCLUDED.ema50,
                    vwap = EXCLUDED.vwap,
                    is_bullish = EXCLUDED.is_bullish,
                    failure_reason = EXCLUDED.failure_reason,
                    timestamp = EXCLUDED.timestamp
            """, data)
        conn.commit()
    except Exception as e:
        logger.error(f"Error in upsert_screener_cache: {e}")
    finally:
        if conn:
            conn.close()

def upsert_premarket_cache(symbol, change_pct):
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO day_trading_screener.premarket_cache (symbol, pre_market_change_pct, timestamp)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (symbol) DO UPDATE SET
                    pre_market_change_pct = EXCLUDED.pre_market_change_pct,
                    timestamp = EXCLUDED.timestamp
            """, (symbol, change_pct))
        conn.commit()
    except Exception as e:
        logger.error(f"Error in upsert_premarket_cache: {e}")
    finally:
        if conn:
            conn.close()
