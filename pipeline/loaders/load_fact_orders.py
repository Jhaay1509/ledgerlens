from pipeline.utils import get_data, get_bigquery_client
from pipeline.constants import COUNTRY_MAP

sql = """
    SELECT 
        o.order_key,
        o.order_id,
        o.customer_id,
        o.order_date,
        o.product_id,
        o.currency,
        o.amount_charged,
        o.number_of_items,
        o.total_paid,
        o.status AS order_status,
        o.is_paid,
        ev.utm_source,
        ev.utm_medium,
        ev.utm_campaign
    FROM canonical_orders o
    LEFT JOIN stg_events ev ON o.order_id = ev.order_id
"""

def load_fact_orders():
    """Extract orders with attribution context and load into BigQuery fact_orders."""
    client = get_bigquery_client()

    # Build product lookup from BigQuery dim_product
    product_data = client.query(
        "SELECT product_key, product_id FROM `my-project-altschool.ledgerlens.dim_product`"
    ).result()
    PRODUCT_MAP = {row["product_id"]: row["product_key"] for row in product_data}

    # Build attribution lookup from BigQuery dim_attribution
    attribution_data = client.query("""
        SELECT attribution_key, utm_source, utm_medium, utm_campaign
        FROM `my-project-altschool.ledgerlens.dim_attribution`
    """).result()
    ATTRIBUTION_MAP = {
        (row["utm_source"], row["utm_medium"], row["utm_campaign"]): row["attribution_key"]
        for row in attribution_data
    }

    # Fetch order data with attribution context from Postgres
    data = get_data(sql)
    rows = []

    for row in data:
        rows.append({
            "order_key":      row["order_key"],
            "order_id":       row["order_id"],
            "customer_id":    row["customer_id"],
            "date_key":       str(row["order_date"].date()),
            "product_key": PRODUCT_MAP[row["product_id"]],
            "country_key":    COUNTRY_MAP[row["currency"].strip()]["country_key"],
            "attribution_key": ATTRIBUTION_MAP.get(
                (row["utm_source"], row["utm_medium"], row["utm_campaign"])
            ),
            "amount_charged": float(row["amount_charged"]),
            "number_of_items": row["number_of_items"],
            "total_paid":     float(row["total_paid"]),
            "order_status":   row["order_status"],
            "is_paid":        row["is_paid"]
        })

    errors = client.insert_rows_json(
        "my-project-altschool.ledgerlens.fact_orders",
        rows
    )

    if errors:
        print(f"Errors loading fact_orders: {errors}")
    else:
        print(f"{len(rows)} rows loaded into fact_orders successfully")

if __name__ == "__main__":
    load_fact_orders()