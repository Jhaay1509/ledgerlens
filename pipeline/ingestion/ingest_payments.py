from pipeline.utils import get_connection

copy_sql = """
    COPY stg_payments(payment_id, provider, amount, currency,
    status, order_id, timestamp)
    FROM STDIN WITH (FORMAT CSV, HEADER, DELIMITER ',')
"""
    
    

def ingest_payments_data():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Clear staging table first — ensures idempotency
            cur.execute("TRUNCATE TABLE stg_payments")
            
            # Load fresh data
            with open("data/raw/raw_payments.csv", "r") as f:
                cur.copy_expert(sql=copy_sql, file=f)
                
        conn.commit()
    print("raw_payments successfully ingested into stg_payments")
    


if __name__ == "__main__":
    ingest_payments_data()