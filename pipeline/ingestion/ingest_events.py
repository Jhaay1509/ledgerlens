import json
import psycopg2.extras
from pipeline.utils import get_connection


sql = """
INSERT INTO stg_events (event_id, session_id, order_id, timestamp, 
                        utm_source, referrer, utm_medium, utm_campaign)
                        VALUES %s
"""
def ingest_event_data():
    with get_connection() as conn:
        with conn.cursor() as cur:

            #Clear staging table first - ensures idempotency
            cur.execute("TRUNCATE TABLE stg_events")

            #Load fresh data
            with open("data/raw/raw_events.json", "r") as f:
                data = json.load(f)
                rows = [(row["event_id"],
                        row["session_id"],
                        row["order_id"],
                        str(row["timestamp"]),     
                        row.get("utm_source"),    
                        row.get("referrer"),
                        row.get("utm_medium"),
                        row.get("utm_campaign")
                        ) for row in data]
            psycopg2.extras.execute_values(cur, sql, rows)
        conn.commit()
    print(f"{len(rows)} entries from raw_events.json ingested into stg_events table")

if __name__ == "__main__":
    ingest_event_data()