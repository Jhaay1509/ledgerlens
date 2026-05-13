def deduplicate_orders(data):
    """Remove duplicate orders using order_id as the uniqueness key.
    
    Commerce systems can resend order records on updates or retries.
    A dictionary keyed by order_id ensures each order appears exactly once.
    Last write wins — preserving the most recent version of each order.
    
    Returns a list of unique order dictionaries.
    """
    seen = {}
    for row in data:
        # order_id is the natural business key — unique per order
        # in the commerce system
        seen[row["order_id"]] = row

    return list(seen.values())
    