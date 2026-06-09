import os
from datetime import date, timedelta
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

def generate_dim_date(start_date, end_date):
    rows = []
    current = start_date
    while current <= end_date:
        rows.append({
            "date_key":         str(current),
            "year":             current.year,
            "quarter":          (current.month - 1) // 3 + 1,
            "month_num":        current.month,
            "month_name":       current.strftime("%B"),
            "week_num":         current.isocalendar()[1],
            "day_of_month":     current.day,
            "day_of_week_num":  current.weekday(),
            "day_of_week_name": current.strftime("%A"),
            "is_weekend":       current.weekday() >= 5
        })
        current += timedelta(days=1)
    return rows

def load_dim_date():
    """Generate date dimension and load into BigQuery."""
    client = bigquery.Client(project="my-project-altschool")

    start_date = date(2020, 1, 1)
    end_date   = date(2030, 12, 31)

    rows = generate_dim_date(start_date, end_date)

    errors = client.insert_rows_json(
        "my-project-altschool.ledgerlens.dim_date",
        rows
    )

    if errors:
        print(f"Errors loading dim_date: {errors}")
    else:
        print(f"{len(rows)} rows loaded into dim_date successfully")

if __name__ == "__main__":
    load_dim_date()