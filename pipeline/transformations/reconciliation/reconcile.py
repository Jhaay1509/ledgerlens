import uuid
from datetime import timedelta
from decimal import Decimal
from pipeline.utils import get_connection, get_data

GET_ORDERS_SQL = " SELECT * FROM canonical_orders"

GET_PAYMENTS_SQL = "SELECT * FROM canonical_payments"


def find_payment_by_reference(order, payments):
    for payment in payments:
        if payment["payment_id"] == order["payment_reference"]:
            return payment
    return None

def find_payment_by_order_id(order, payments):
    for payment in payments:
        if payment["order_id"]== order["order_id"]:
            return payment
    return None

def find_payment_by_amount_time(order, payments):
    for payment in payments:
        time_diff= abs(order["order_date"] - payment["paid_at"])
        if payment["amount"]== order["amount_charged"] and \
        time_diff <= timedelta(minutes= 5):
            return payment
    return None


def update_order(cur, order, payment):
    """Update canonical_orders with reconciliation outcome after a match is found."""
    sql = """
        UPDATE canonical_orders
        SET successful_payment_key = %s,
            is_paid = TRUE,
            total_paid = %s,
            updated_at = NOW()
        WHERE order_id = %s
    """
    cur.execute(sql, (
        payment["payment_key"],   # successful_payment_key
        payment["amount"],        # total_paid
        order["order_id"]         # identifies which order to update
    ))

def update_payment(cur, payment, match_method, match_confidence):
    """Update canonical_payments with reconciliation outcome after a match is found.
    
    Stores how the match was made (match_method) and how confident
    we are in that match (match_confidence) for auditability.
    Finance can use these fields to assess the reliability of any
    revenue figure.
    """
    sql = """
        UPDATE canonical_payments
        SET match_method     = %s,
            match_confidence = %s,
            updated_at       = NOW()
        WHERE payment_id = %s
        AND provider     = %s
    """
    # WHERE uses both payment_id and provider — the composite unique key
    # if two providers share the same payment_id format
    cur.execute(sql, (
        match_method,           # which rule fired e.g 'direct_id_match'
        match_confidence,       # confidence score e.g 1.0, 0.8
        payment["payment_id"],  # identifies which payment to update
        payment["provider"]     # combined with payment_id for precision
    ))

def log_reconciliation(cur, payment, order, match_method, 
                       match_confidence, status, failure_reason=None):
    """Write an immutable record of every reconciliation attempt.
    
    Called for both successful matches and failures.
    failure_reason is None when status is 'matched'.
    order is None when payment is orphaned.
    """
    sql = """
        INSERT INTO reconciliation_log (
            reconciliation_id, payment_key, order_key,
            match_method, match_confidence,
            reconciliation_status, failure_reason
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    reconciliation_id = f"REC-{uuid.uuid4().hex[:8].upper()}"

    cur.execute(sql, (
        reconciliation_id,
        payment["payment_key"] if payment is not None else None,
        order["order_key"],
        match_method,
        match_confidence,
        status,
        failure_reason
    ))


def reconcile(orders, payments):
    """Run reconciliation priority ladder for every order.
    
    Rules run in order — deterministic first, fuzzy fallback, then orphan.
    Every attempt is logged to reconciliation_log regardless of outcome.
    One connection shared across all operations for transaction integrity.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            for order in orders:

                # ── Rule 1 — Direct payment reference match
                payment = find_payment_by_reference(order, payments)
                if payment:
                    update_order(cur, order, payment)
                    update_payment(cur, payment, "direct_id_match", Decimal("1.0"))
                    log_reconciliation(cur, payment, order,
                                      "direct_id_match", Decimal("1.0"),
                                      "matched")
                    continue

                # ── Rule 2 — Order ID match
                payment = find_payment_by_order_id(order, payments)
                if payment:
                    update_order(cur, order, payment)
                    update_payment(cur, payment, "order_id_match", Decimal("1.0"))
                    log_reconciliation(cur, payment, order,
                                      "order_id_match", Decimal("1.0"),
                                      "matched")
                    continue

                # ── Rule 3 — Fuzzy match — amount and time window
                payment = find_payment_by_amount_time(order, payments)
                if payment:
                    update_order(cur, order, payment)
                    update_payment(cur, payment, "amount_time_only", Decimal("0.8"))
                    log_reconciliation(cur, payment, order,
                                      "amount_time_only", Decimal("0.8"),
                                      "matched")
                    continue

                # ── Rule 4 — No match found — order remains unreconciled
                log_reconciliation(cur, None, order,
                                  "unmatched", Decimal("0.0"),
                                  "unmatched",
                                  failure_reason="no_match_found")

        conn.commit()
        print("Reconciliation complete")

if __name__== "__main__":
    order_dict = get_data(GET_ORDERS_SQL)
    payment_dict = get_data(GET_PAYMENTS_SQL)
    reconcile(order_dict, payment_dict)