import os
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/service_account.json"

client = bigquery.Client(project="my-project-altschool")

SQL_FILES = [
    "sql/bigquery/dim_date.sql",
    "sql/bigquery/dim_product.sql",
    "sql/bigquery/dim_country.sql",
    "sql/bigquery/dim_attribution.sql",
    "sql/bigquery/fact_payments.sql",
    "sql/bigquery/fact_orders.sql",
    "sql/bigquery/daily_revenue.sql",
]

for sql_file in SQL_FILES:
    with open(sql_file, "r") as f:
        sql = f.read()
    query_job = client.query(sql)
    query_job.result()
    print(f"Created table from {sql_file}")

print("All BigQuery tables created successfully")