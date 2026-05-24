import psycopg2.extras
from pipeline.utils import get_connection
from pipeline.transformations.orders.normalise_orders import normalise_order
from pipeline.transformations.orders.deduplicate_orders import deduplicate_orders

# ── SQL ───────────────────────────────────────────────────────────────────────
# ON CONFLICT DO NOTHING ensures idempotency — pipeline reruns
# won't duplicate records already loaded into canonical_orders
sql = """
    INSERT INTO canonical_orders (
        order_id, customer_id, product_id,
        payment_reference,
        status, currency, number_of_items,
        amount_charged, successful_payment_key, is_paid,
        total_paid, order_date
    ) VALUES %s
    ON CONFLICT (order_id) DO NOTHING
"""

# ── Load function ─────────────────────────────────────────────────────────────

def load_canonical_orders(cleaned_data):
    """Load deduplicated, normalised orders into canonical_orders.
    
    Reconciliation outcome fields (successful_payment_key, is_paid, total_paid)
    are pre-set to defaults by the normalisation layer and will be updated
    by the reconciliation script after payments are matched.
    """
    # Convert list of dictionaries to list of tuples
    # Column order must match INSERT statement exactly
    rows = [(
        row["order_id"],
        row["customer_id"],
        row["product_id"],
        row["payment_reference"],
        row["status"],
        row["currency"],
        row["number_of_items"],
        row["amount_charged"],
        row["successful_payment_key"],  # None until reconciliation runs
        row["is_paid"],                 # False until successful payment matched
        row["total_paid"],              # 0 until reconciliation runs
        row["timestamp"]                # order_date in canonical table
    ) for row in cleaned_data]

    with get_connection() as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(cur, sql, rows)
        conn.commit()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    normalised_data = normalise_order()
    cleaned_data = deduplicate_orders(normalised_data)
    load_canonical_orders(cleaned_data)
    print(f"{len(cleaned_data)} orders successfully loaded into canonical_orders")


  
 