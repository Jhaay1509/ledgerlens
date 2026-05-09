import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_connection(): 
    return psycopg2.connect(
        host= os.getenv("DB_HOST"),
        port= os.getenv("DB_PORT"),
        dbname= os.getenv("DB_NAME"),
        user= os.getenv("DB_USER"),
        password= os.getenv("PASSWORD")
    )

def get_data(sql):
    with get_connection() as conn:
            with conn.cursor(cursor_factory= RealDictCursor) as cur:
                cur.execute(sql)
                data = cur.fetchall()
    return data
