from pipeline.utils import get_data
from pipeline.transformations.payments.normalise_payments import normalise_payment
from pipeline.transformations.payments.deduplicate_payments import deduplicate_payments
from pipeline.transformations.payments.load_canonical_payments import load_canonical_payments
from pipeline.transformations.orders.normalise_orders import normalise_order
from pipeline.transformations.orders.deduplicate_orders import deduplicate_orders
from pipeline.transformations.orders.load_canonical_orders import load_canonical_orders
from pipeline.transformations.reconciliation.reconcile import reconcile
from pipeline.transformations.refunds.apply_refunds import apply_refunds

def run_payment_pipeline():
    """Normalise, deduplicate and load payments to canonical table."""
    normalised = normalise_payment()
    deduplicated = deduplicate_payments(normalised)
    load_canonical_payments(deduplicated)

def run_order_pipeline():
    """Normalise, deduplicate and load orders to canonical table."""
    normalised = normalise_order()
    deduplicated = deduplicate_orders(normalised)
    load_canonical_orders(deduplicated)

def run_reconciliation():
    """Fetch canonical data and run reconciliation."""
    orders = get_data("SELECT * FROM canonical_orders")
    payments = get_data("SELECT * FROM canonical_payments")
    reconcile(orders, payments)

def run_apply_refunds():
    """Apply refunds to canonical payments."""
    apply_refunds()