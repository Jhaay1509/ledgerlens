import json
import psycopg2.extras
from pipeline.utils import get_connection


sql = """
INSERT INTO stg_orders(order_id, customer_id, product_id,product_name,
                    payment_reference, currency, status,
                    number_of_items, amount_charged, timestamp)
                    VALUES %s
"""
def ingest_orders_data():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Clear staging table first — ensures idempotency
            cur.execute("TRUNCATE TABLE stg_orders")

            # Load fresh data
            with open("data/raw/raw_orders.json", "r") as f:
                data= json.load(f)
                
                rows = [(row["order_id"],
                row["customer_id"],
                row["product_id"],
                row["product_name"],
                row.get("payment_reference"),
                row["currency"],
                row["status"],
                row["number_of_items"],
                row["amount_charged"],
                str(row["timestamp"]))for row in data]
            
            
            psycopg2.extras.execute_values(cur, sql, rows)
        conn.commit()
    print(f"{len(rows)} rows from raw_orders.json were inserted into stg_orders table")

if __name__ == "__main__":
    ingest_orders_data()