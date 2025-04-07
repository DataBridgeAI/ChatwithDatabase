from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryGetDatasetOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.utils.dates import days_ago
import json
import logging

from schema_processor import get_table_schema, upload_to_gcs

# Define default args
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
BUCKET_NAME = "bigquery-schema-store"
SCHEMA_PATH = 'schema_data'


def extract_and_process_schemas(**kwargs):
    """
    Extract schema data from BigQuery tables and generate schema and statistics files.
    """
    from google.cloud import bigquery
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    bq_client = bigquery.Client(project=PROJECT_ID)
    logger.info(f"Extracting schemas from dataset {DATASET_ID} in project {PROJECT_ID}")
    
    dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"
    tables = list(bq_client.list_tables(dataset_ref))
    
    schemas = {}
    statistics = {}
    
    for table in tables:
        table_id = table.table_id
        logger.info(f"Processing schema for table {table_id}")
        
        try:
            schema = get_table_schema(bq_client, PROJECT_ID, DATASET_ID, table_id)
            schemas[table_id] = schema
            
            query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{table_id}` LIMIT 10000"
            df = bq_client.query(query).to_dataframe()
            
            statistics[table_id] = {
                "row_count": len(df),
                "mean": df.mean(numeric_only=True).to_dict(),
                "std": df.std(numeric_only=True).to_dict(),
                "null_percent": df.isnull().mean().to_dict(),
            }
            
            table_schema_json = json.dumps(schema, indent=2)
            upload_to_gcs(BUCKET_NAME, f"{SCHEMA_PATH}/tables/{table_id}_schema.json", table_schema_json)
        
        except Exception as e:
            logger.error(f"Error processing table {table_id}: {str(e)}")
    
    # Upload raw schema data
    all_schemas_json = json.dumps(schemas, indent=2)
    upload_to_gcs(BUCKET_NAME, f"{SCHEMA_PATH}/all_schemas.json", all_schemas_json)
    
    # Upload data statistics
    data_statistics_json = json.dumps(statistics, indent=2)
    upload_to_gcs(BUCKET_NAME, f"{SCHEMA_PATH}/data_statistics.json", data_statistics_json)
    
    return f"gs://{BUCKET_NAME}/{SCHEMA_PATH}/data_statistics.json"


def validate_schema_output(**kwargs):
    """
    Validates that the schema and statistics files were properly created.
    """
    from google.cloud import storage
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    
    required_files = [
        f"{SCHEMA_PATH}/all_schemas.json",
        f"{SCHEMA_PATH}/data_statistics.json"
    ]
    
    missing_files = [file_path for file_path in required_files if not bucket.blob(file_path).exists()]
    
    if missing_files:
        logger.error(f"Missing schema files: {missing_files}")
        raise ValueError(f"Schema extraction failed. Missing files: {missing_files}")
    
    logger.info("Schema validation successful")
    return True

# Define DAG
dag = DAG(
    'extract_bigquery_schema',
    default_args=default_args,
    description='Extract schema and statistics from BigQuery',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=['nlsql', 'schema'],
)

get_dataset_info = BigQueryGetDatasetOperator(
    task_id='get_dataset_info',
    dataset_id=DATASET_ID,
    project_id=PROJECT_ID,
    dag=dag
)

process_schemas = PythonOperator(
    task_id='process_schemas',
    python_callable=extract_and_process_schemas,
    provide_context=True,
    dag=dag
)

validate_schemas = PythonOperator(
    task_id='validate_schemas',
    python_callable=validate_schema_output,
    provide_context=True,
    dag=dag
)

send_slack_notification = SlackWebhookOperator(
    task_id='send_slack_notification',
    slack_webhook_conn_id='slack_webhook',
    message="✅ Airflow DAG `extract_bigquery_schema` completed successfully!",
    channel="#airflow-notifications",
    username="airflow-bot",
    dag=dag
)

# Task dependencies
get_dataset_info >> process_schemas >> validate_schemas >> send_slack_notification
