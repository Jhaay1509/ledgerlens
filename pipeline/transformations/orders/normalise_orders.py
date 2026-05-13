from decimal import Decimal
from datetime import datetime, timezone
from pipeline.utils import get_data

# ── Query ─────────────────────────────────────────────────────────────────────
sql = "SELECT * FROM stg_orders"

# ── Status mapping ────────────────────────────────────────────────────────────
# Maps raw commerce system values to canonical ENUM values
# Handles inconsistent casing from upstream systems
ORDER_STATUS_MAP = {
    "processing":  "processing",
    "Processing":  "processing",
    "PROCESSING":  "processing",
    "shipped":     "shipped",
    "Shipped":     "shipped",
    "completed":   "completed",
    "Complete":    "completed",
    "COMPLETED":   "completed",
    "cancelled":   "cancelled",
    "Canceled":    "cancelled",
}

# ── Normalisation functions ───────────────────────────────────────────────────

def normalise_status(raw_status):
    """Map raw order status to canonical ENUM value.
    Defaults to 'processing' if status is unrecognised."""
    return ORDER_STATUS_MAP.get(raw_status, "processing")


def normalise_timestamp(ts):
    """Convert order timestamp string to timezone-aware datetime object.
    Handles ISO format (Stripe-style) and fallback datetime format (PayPal-style)."""
    try:
        # Primary — ISO 8601 format e.g "2024-01-15T10:30:00Z"
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        # Fallback — datetime string format e.g "15/01/2024 10:30"
        return datetime.strptime(ts, "%d/%m/%Y %H:%M").replace(tzinfo=timezone.utc)


# ── Main normalisation function ───────────────────────────────────────────────

def normalise_order():
    """Fetch raw orders from staging and normalise all fields.
    
    Reconciliation outcome fields (successful_payment_key, is_paid, total_paid)
    are initialised with defaults here and updated later by reconciliation scripts.
    
    Returns a list of normalised order dictionaries.
    """
    raw_orders = get_data(sql)

    orders = [{
        # ── Identity
        "order_id":               row["order_id"],
        "customer_id":            row["customer_id"],
        "product_id":             row["product_id"],
        "product_name":           row["product_name"],

        # ── Payment linkage (nullable — not all orders have a payment reference)
        "payment_reference":      row.get("payment_reference"),

        # ── Order details — normalised types
        "status":                 normalise_status(row["status"]),
        "currency":               row["currency"].strip().upper(),
        "number_of_items":        int(row["number_of_items"]),
        "amount_charged":         Decimal(row["amount_charged"]),

        # ── Reconciliation outcome — defaults until reconciliation runs
        "successful_payment_key": None,   # populated after reconciliation
        "is_paid":                False,  # flipped to True after successful match
        "total_paid":             0,      # updated after reconciliation

        # ── Timing
        "timestamp":              normalise_timestamp(row["timestamp"]),

    } for row in raw_orders]

    return orders


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = normalise_order()
    print(f"{len(result)} orders normalised successfully")