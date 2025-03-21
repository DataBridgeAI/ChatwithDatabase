from google.cloud import bigquery, storage
import json
import pandas as pd
import numpy as np
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

# Constants
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
BUCKET_NAME = "bigquery-schema-store"
SCHEMA_PATH = "schema_data"
STATISTICS_FILE = "data_statistics.json"
SLACK_CONN_ID = "slack_webhook"

def check_schema_drift(**kwargs):
    """Detects schema drift by comparing the latest schema with the stored schema."""
    bq_client = bigquery.Client(project=PROJECT_ID)
    storage_client = storage.Client()

    dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"
    tables = list(bq_client.list_tables(dataset_ref))
    
    current_schema = {}
    for table in tables:
        table_id = table.table_id
        schema = {field.name: field.field_type for field in bq_client.get_table(f"{dataset_ref}.{table_id}").schema}
        current_schema[table_id] = schema

    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"{SCHEMA_PATH}/all_schemas.json")

    if not blob.exists():
        raise ValueError("Previous schema not found. Run schema extraction first.")

    previous_schema = json.loads(blob.download_as_text())

    schema_drift = {}
    for table, schema in current_schema.items():
        if table in previous_schema and schema != previous_schema[table]:
            schema_drift[table] = {"previous": previous_schema[table], "current": schema}

    if schema_drift:
        message = f"⚠️ Schema Drift Detected: {json.dumps(schema_drift, indent=2)}"
        kwargs["ti"].xcom_push(key="schema_drift_alert", value=message)

def check_data_drift(**kwargs):
    """Detects data drift by comparing current statistics with historical ones."""
    bq_client = bigquery.Client(project=PROJECT_ID)
    storage_client = storage.Client()

    dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"
    tables = list(bq_client.list_tables(dataset_ref))

    data_statistics = {}
    for table in tables:
        table_id = table.table_id
        query = f"SELECT * FROM `{dataset_ref}.{table_id}` LIMIT 1000"
        df = bq_client.query(query).to_dataframe()

        data_statistics[table_id] = {
            "row_count": len(df),
            "mean": df.mean(numeric_only=True).to_dict(),
            "std": df.std(numeric_only=True).to_dict(),
            "null_percent": df.isnull().mean().to_dict(),
        }

    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"{SCHEMA_PATH}/{STATISTICS_FILE}")

    if not blob.exists():
        raise ValueError("Previous statistics not found. Run schema extraction first.")

    previous_statistics = json.loads(blob.download_as_text())

    data_drift_detected = {}
    for table, stats in data_statistics.items():
        if table in previous_statistics:
            for metric in ["mean", "std", "null_percent"]:
                for column, value in stats[metric].items():
                    prev_value = previous_statistics[table].get(metric, {}).get(column)
                    if prev_value is not None and abs(value - prev_value) > 0.1 * abs(prev_value):
                        data_drift_detected.setdefault(table, {})[column] = {
                            "previous": prev_value,
                            "current": value,
                        }

    if data_drift_detected:
        message = f"⚠️ Data Drift Detected: {json.dumps(data_drift_detected, indent=2)}"
        kwargs["ti"].xcom_push(key="data_drift_alert", value=message)

def send_slack_alert(**kwargs):
    """Sends a Slack notification if any drift is detected."""
    schema_alert = kwargs["ti"].xcom_pull(task_ids="check_schema_drift", key="schema_drift_alert")
    data_alert = kwargs["ti"].xcom_pull(task_ids="check_data_drift", key="data_drift_alert")

    if schema_alert or data_alert:
        message = schema_alert or data_alert
        slack_alert = SlackWebhookOperator(
            task_id="slack_notification",
            slack_webhook_conn_id=SLACK_CONN_ID,
            message=message,
            channel="#airflow-notifications",
            username="airflow-bot",
            dag=kwargs["dag"],
        )
        slack_alert.execute(kwargs)
