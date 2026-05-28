from psycopg2.extras import RealDictCursor
from decimal import Decimal
from pipeline.utils import get_data, get_connection

def get_payment_key(cur, payment_id):
    """Look up surrogate payment_key using natural payment_id."""
    cur.execute("""
        SELECT payment_key, amount, refund_total, provider 
        FROM canonical_payments 
        WHERE payment_id = %s
    """, (payment_id,))
    return cur.fetchone()

def insert_refund_event(cur, refund, payment_key):
    """Insert one refund record into refund_events."""
    cur.execute("""
        INSERT INTO refund_events (
            refund_id, payment_key, refund_amount,
            refund_type, refund_reason, refunded_at
        ) VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (refund_id) DO NOTHING
    """, (
        refund["refund_id"],
        payment_key,
        Decimal(refund["refund_amount"]),
        refund["refund_type"],
        refund.get("reason"),
        refund["refund_date"]
    ))

def update_payment_amounts(cur, payment_key, refund_amount, current_amount, current_refund_total):
    """Update refund_total and net_amount on canonical_payments."""
    new_refund_total = Decimal(str(current_refund_total)) + Decimal(str(refund_amount))
    new_net_amount   = Decimal(str(current_amount)) - new_refund_total

    cur.execute("""
        UPDATE canonical_payments
        SET refund_total = %s,
            net_amount   = %s,
            updated_at   = NOW()
        WHERE payment_key = %s
    """, (new_refund_total, new_net_amount, payment_key))

def apply_refunds():
    """Process all raw refunds from staging.
    
    For each refund:
    1. Find the matching payment in canonical_payments
    2. Insert into refund_events
    3. Update refund_total and net_amount on canonical_payments
    """
    refunds = get_data("SELECT * FROM stg_refunds")

    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            for refund in refunds:

                # Step 1 — find matching payment
                payment = get_payment_key(cur, refund["payment_id"])

                if payment is None:
                    print(f"Warning: No payment found for refund {refund['refund_id']}")
                    continue

                payment_key           = payment["payment_key"]
                current_amount        = payment["amount"]
                current_refund_total  = payment["refund_total"]
                provider = payment["provider"]


                # Normalise refund amount based on provider
                raw_amount = Decimal(refund["refund_amount"])
                refund_amount = raw_amount / 100 if provider == "fastpay" else raw_amount
 
                # Step 2 — insert refund record
                insert_refund_event(cur, refund, payment_key)

                # Step 3 — update payment amounts
                update_payment_amounts(
                    cur, payment_key,
                    refund_amount,
                    current_amount,
                    current_refund_total
                )

        conn.commit()
        print(f"{len(refunds)} refunds applied successfully")

if __name__ == "__main__":
    apply_refunds()