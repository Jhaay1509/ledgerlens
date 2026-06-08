from google.cloud import bigquery
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/service_account.json"

client = bigquery.Client(project="my-project-altschool")
dataset = bigquery.Dataset("my-project-altschool.ledgerlens")
dataset.location = "EU"
client.create_dataset(dataset, exists_ok=True)
print("Dataset created successfully")