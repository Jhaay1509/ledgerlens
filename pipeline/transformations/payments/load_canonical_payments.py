import psycopg2
import psycopg2.extras
from pipeline.utils import get_connection
from pipeline.transformations.payments.normalise_payments import normalise_payment
from pipeline.transformations.payments.deduplicate_payments import deduplicate_payments

sql = """
    INSERT INTO canonical_payments (
        payment_id, provider, amount, refund_total, net_amount,
        currency, status, is_retry, order_id, paid_at,
        match_method, match_confidence
    ) VALUES %s
    ON CONFLICT (provider, payment_id) DO NOTHING
"""

def load_canonical_payments(data):
    rows = [(
        row["payment_id"],
        row["provider"],
        row["amount"],
        0,                    # refund_total
        row["amount"],        # net_amount
        row["currency"],
        row["status"],
        False,                # is_retry
        row.get("order_id"),
        row["timestamp"],     # paid_at
        None,                 # match_method
        None                  # match_confidence
    ) for row in data]

    with get_connection() as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(cur, sql, rows)
        conn.commit()

if __name__ == "__main__":
    normalised_data = normalise_payment()
    cleaned_data = deduplicate_payments(normalised_data)
    load_canonical_payments(cleaned_data)
    print(f"{len(cleaned_data)} payments inserted into canonical_payments")