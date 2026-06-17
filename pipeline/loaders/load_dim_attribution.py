from pipeline.utils import get_data, get_bigquery_client

PRIMARY_SOURCE_MAP = {
    "cpc":     "paid",
    "organic": "organic",
    "social":  "referral",
    "email":   "email",
    "none":    "direct"     # "none" is the literal utm_medium string, not Python None
}

sql = """
    SELECT DISTINCT utm_source, utm_medium, utm_campaign, referrer
    FROM stg_events
"""

def load_dim_attribution():
    """Fetch unique attribution combinations and load into BigQuery."""
    data = get_data(sql)
    rows = []

    for index, row in enumerate(data, start=1):
        rows.append({
            "attribution_key": index,
            "primary_source":  PRIMARY_SOURCE_MAP[row["utm_medium"]],
            "media_source":    row["utm_source"],
            "campaign_name":   row["utm_campaign"],
            "referral_code":   None,
            "utm_source":      row["utm_source"],
            "utm_medium":      row["utm_medium"],
            "utm_campaign":    row["utm_campaign"]
        })

    client = get_bigquery_client()
    errors = client.insert_rows_json(
        "my-project-altschool.ledgerlens.dim_attribution",
        rows
    )

    if errors:
        print(f"Errors loading dim_attribution: {errors}")
    else:
        print(f"{len(rows)} rows loaded into dim_attribution successfully")

if __name__ == "__main__":
    load_dim_attribution()