import os
import psycopg2
from dotenv import load_dotenv
from db import get_connection

load_dotenv()

def test_can_connect_to_db():
    conn = None
    try:
        conn = get_connection()
        assert conn is not None
    finally:
        if conn:
            conn.close()
