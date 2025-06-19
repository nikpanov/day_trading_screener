import os
import psycopg2
from dotenv import load_dotenv
from db import get_connection


def main():
    try:
        conn = get_connection()
        print("✅ Connected to PostgreSQL.")
        with conn.cursor() as cur:
            cur.execute("SELECT run_id, run_timestamp FROM day_trading_screener.screener_run ORDER BY run_timestamp DESC LIMIT 5;")
            rows = cur.fetchall()
            print("📄 Last 5 screener runs:")
            for row in rows:
                print(f"Run ID: {row[0]}, Time: {row[1]}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
