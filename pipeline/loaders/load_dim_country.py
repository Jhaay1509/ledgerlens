from pipeline.utils import get_bigquery_client
from pipeline.constants import COUNTRY_MAP

def generate_country_data():
    """Build dim_country rows from the COUNTRY_MAP lookup."""
    country_list = []

    for currency, country in COUNTRY_MAP.items():
        country_list.append({
            "country_key":  country["country_key"],
            "country_name": country["country_name"],
            "country_code": country["country_code"],
            "state":        country["state"],
            "region":       country["region"]
        })
    return country_list


def load_dim_country():
    """Load country dimension into BigQuery."""
    client = get_bigquery_client()
    rows = generate_country_data()

    errors = client.insert_rows_json(
        "my-project-altschool.ledgerlens.dim_country",
        rows
    )

    if errors:
        print(f"Errors loading dim_country: {errors}")
    else:
        print(f"{len(rows)} rows loaded into dim_country successfully")


if __name__ == "__main__":
    load_dim_country()