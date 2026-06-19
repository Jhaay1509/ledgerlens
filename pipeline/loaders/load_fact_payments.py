from pipeline.utils import get_data, get_bigquery_client
from pipeline.constants import COUNTRY_MAP


sql = """
    SELECT 
        p.payment_key,
        p.payment_id,
        p.provider,
        p.paid_at,
        p.currency,
        p.amount,
        p.net_amount,
        p.refund_total,
        p.status AS payment_status,
        p.is_retry,
        o.product_id,
        ev.utm_source,
        ev.utm_medium,
        ev.utm_campaign
    FROM canonical_payments p
    LEFT JOIN canonical_orders o ON p.order_id = o.order_id
    LEFT JOIN stg_events ev ON p.order_id = ev.order_id
"""


def load_fact_payments():
    """Extract payments with order and attribution context, load into BigQuery fact_payments."""
    client = get_bigquery_client()

    # Build product lookup from BigQuery dim_product
    product_data = client.query("""
        SELECT product_key, product_id
        FROM `my-project-altschool.ledgerlens.dim_product`
    """).result()
    PRODUCT_MAP = {row["product_id"]: row["product_key"] for row in product_data}

    # Build attribution lookup from BigQuery dim_attribution
    attr_data = client.query("""
        SELECT attribution_key, utm_source, utm_medium, utm_campaign
        FROM `my-project-altschool.ledgerlens.dim_attribution`
    """).result()
    ATTRIBUTION_MAP = {
        (row["utm_source"], row["utm_medium"], row["utm_campaign"]): row["attribution_key"]
        for row in attr_data
    }

    # Fetch payment data with order and event context from Postgres
    data = get_data(sql)
    rows = []

    for row in data:
        rows.append({
            "payment_key":    row["payment_key"],
            "payment_id":     row["payment_id"],
            "provider":       row["provider"],
            "date_key":       str(row["paid_at"].date()),
            "product_key":    PRODUCT_MAP.get(row["product_id"]),
            "country_key":    COUNTRY_MAP[row["currency"].strip()]["country_key"],
            "attribution_key": ATTRIBUTION_MAP.get(
                (row["utm_source"], row["utm_medium"], row["utm_campaign"])
            ),
            "amount":         float(row["amount"]),
            "net_amount":     float(row["net_amount"]),
            "refund_total":   float(row["refund_total"]),
            "currency":       row["currency"].strip(),
            "payment_status": row["payment_status"],
            "is_retry":       row["is_retry"]
        })

    errors = client.insert_rows_json(
        "my-project-altschool.ledgerlens.fact_payments",
        rows
    )

    if errors:
        print(f"Errors loading fact_payments: {errors}")
    else:
        print(f"{len(rows)} rows loaded into fact_payments successfully")


if __name__ == "__main__":
    load_fact_payments()