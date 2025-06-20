from db import get_connection
from utils.logger import setup_logger
from api.fmp_client import fetch_core_screener

logger = setup_logger()

def import_tickers_from_fmp(limit=1000):
    tickers = fetch_core_screener(limit)
    conn = get_connection()
    cursor = conn.cursor()
    inserted, skipped = 0, 0

    for item in tickers:
        symbol = item.get("symbol", "").strip().upper()
        if not symbol:
            continue
        try:
            cursor.execute("""
                INSERT INTO day_trading_screener.ticker_rotation (symbol)
                VALUES (%s)
                ON CONFLICT (symbol) DO NOTHING;
            """, (symbol,))
            if cursor.rowcount:
                inserted += 1
            else:                skipped += 1
        except Exception as e:
            logger.error(f"Error inserting {symbol}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"Imported from FMP: {inserted} inserted, {skipped} skipped")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1000, help="Max tickers to import from FMP")
    args = parser.parse_args()

    import_tickers_from_fmp(limit=args.limit)
