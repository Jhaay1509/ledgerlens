import os
from datetime import date
from dotenv import load_dotenv
from google.cloud import bigquery
from scripts.generate_data import PRODUCTS
from pipeline.utils import get_bigquery_client

load_dotenv()

CATEGORY_MAP = {
    "PROD-001": "subscription",
    "PROD-002": "subscription",
    "PROD-003": "subscription",
    "PROD-004": "one_off_purchase",
    "PROD-005": "one_off_purchase",
}

def generate_dim_product(products):
    """Generate dim_product rows from product catalogue.
    
    Uses Type 2 SCD pattern — each product gets one current version row.
    valid_to is NULL meaning still active. product_key is generated here
    since BigQuery has no auto-increment.
    """
    rows = []
    for key, product in enumerate(products, start=1):
        rows.append({
            "product_key":      key,
            "product_id":       product["product_id"],
            "product_name":     product["product_name"],
            "product_category": CATEGORY_MAP.get(product["product_id"], "one_off_purchase"),
            "price":            product["price"],
            "currency":         "GBP",
            "valid_from":       str(date.today()),
            "valid_to":         None,
            "is_current":       True
        })
    return rows

def load_dim_product():
    """Load product dimension into BigQuery."""
    client = get_bigquery_client()
    rows = generate_dim_product(PRODUCTS)

    errors = client.insert_rows_json(
        "my-project-altschool.ledgerlens.dim_product",
        rows
    )

    if errors:
        print(f"Errors loading dim_product: {errors}")
    else:
        print(f"{len(rows)} rows loaded into dim_product successfully")

if __name__ == "__main__":
    load_dim_product()