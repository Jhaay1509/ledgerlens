from pipeline.utils import get_connection

copy_sql = """
COPY stg_refunds (refund_id,payment_id,refund_amount,refund_type,reason,refund_date)
FROM STDIN WITH (FORMAT CSV, HEADER, DELIMITER ',')
"""

def ingest_refund_data():
    with get_connection() as conn:
        with conn.cursor() as cur:

            # Clear staging table first — ensures idempotency
            cur.execute("TRUNCATE TABLE stg_refunds")

            #Load fresh data
            with open("data/raw/raw_refunds.csv", "r") as f:
                cur.copy_expert(copy_sql,f)
        conn.commit()
    print("data from raw_refunds successfully ingested into stg_refunds.csv")


if __name__ == "__main__":
    ingest_refund_data()