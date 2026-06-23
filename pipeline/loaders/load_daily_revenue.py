from pipeline.utils import get_bigquery_client

sql = """
WITH payment_agg AS (
    SELECT
        date_key,
        country_key,
        product_key,
        attribution_key,
        SUM(amount)        AS gross_revenue,
        SUM(refund_total)  AS refunds,
        SUM(net_amount)    AS net_revenue,
        COUNT(payment_key) AS payment_count
    FROM `my-project-altschool.ledgerlens.fact_payments`
    WHERE product_key IS NOT NULL
    GROUP BY date_key, country_key, product_key, attribution_key
),
order_agg AS (
    SELECT
        date_key,
        country_key,
        product_key,
        attribution_key,
        COUNT(order_key) AS order_count
    FROM `my-project-altschool.ledgerlens.fact_orders`
    GROUP BY date_key, country_key, product_key, attribution_key
)
SELECT
    COALESCE(p.date_key, o.date_key)             AS date_key,
    COALESCE(p.country_key, o.country_key)       AS country_key,
    COALESCE(p.product_key, o.product_key)       AS product_key,
    COALESCE(p.attribution_key, o.attribution_key) AS attribution_key,
    COALESCE(p.gross_revenue, 0)                 AS gross_revenue,
    COALESCE(p.refunds, 0)                       AS refunds,
    COALESCE(p.net_revenue, 0)                   AS net_revenue,
    COALESCE(p.payment_count, 0)                 AS payment_count,
    COALESCE(o.order_count, 0)                   AS order_count
FROM payment_agg p
FULL OUTER JOIN order_agg o
    ON  p.date_key        = o.date_key
    AND p.country_key     = o.country_key
    AND p.product_key     = o.product_key
    AND p.attribution_key IS NOT DISTINCT FROM o.attribution_key
"""


def load_daily_revenue():
    """Aggregate payment and order fact tables in BigQuery and load into daily_revenue mart.

    Joins pre-aggregated payment metrics (gross revenue, refunds, net revenue,
    payment count) with order counts, grouped by the four shared dimension keys.
    Surrogate key generated in Python since BigQuery has no auto-increment.
    """
    client = get_bigquery_client()

    # Run aggregation query entirely inside BigQuery — no Postgres involvement
    data = client.query(sql).result()

    rows = []
    for key, row in enumerate(data, start=1):
        rows.append({
            "daily_revenue_key": key,
            "date_key":          str(row["date_key"]),
            "country_key":       row["country_key"],
            "product_key":       row["product_key"],
            "attribution_key":   row["attribution_key"],
            "gross_revenue":     float(row["gross_revenue"]),
            "refunds":           float(row["refunds"]),
            "net_revenue":       float(row["net_revenue"]),
            "payment_count":     row["payment_count"],
            "order_count":       row["order_count"],
        })

    errors = client.insert_rows_json(
        "my-project-altschool.ledgerlens.daily_revenue",
        rows
    )

    if errors:
        print(f"Errors loading daily_revenue: {errors}")
    else:
        print(f"{len(rows)} rows loaded into daily_revenue successfully")


if __name__ == "__main__":
    load_daily_revenue()