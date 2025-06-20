import csv
from db import get_connection
from utils.logger import setup_logger

logger = setup_logger()

def import_tickers_from_csv(csv_path):
    conn = get_connection()
    cursor = conn.cursor()
    inserted, skipped = 0, 0

    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            symbol = row["symbol"].strip().upper()
            try:
                cursor.execute("""
                    INSERT INTO day_trading_screener.ticker_rotation (symbol)
                    VALUES (%s)
                    ON CONFLICT (symbol) DO NOTHING;
                """, (symbol,))
                if cursor.rowcount:
                    inserted += 1
                else:
                    skipped += 1
            except Exception as e:
                logger.error(f"Error inserting {symbol}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    logger.info(f"✅ Import complete: {inserted} inserted, {skipped} skipped")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path", help="Path to CSV file with 'symbol' column")
    args = parser.parse_args()

    import_tickers_from_csv(args.csv_path)
