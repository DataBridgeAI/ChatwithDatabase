# dags/extract_bigquery_schema.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryGetDatasetOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.dates import days_ago
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.models import Variable
import os
import sys
import json
import logging

# Add scripts directory to path to import schema_processor
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../scripts'))
from schema_processor import get_table_schema, format_schema_for_prompt, upload_to_gcs

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
DATASET_ID =  "RetailDataset"
BUCKET_NAME = "bigquery-schema-store"
SCHEMA_PATH = 'schema_data'

def extract_and_process_schemas(**kwargs):
    """
    Extract schema data from BigQuery tables and process for prompts
    """
    from google.cloud import bigquery
    import logging
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Initialize BigQuery client
    bq_client = bigquery.Client(project=PROJECT_ID)
    logger.info(f"Extracting schemas from dataset {DATASET_ID} in project {PROJECT_ID}")
    
    # Get all tables in the dataset
    dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"
    tables = list(bq_client.list_tables(dataset_ref))
    logger.info(f"Found {len(tables)} tables in dataset {DATASET_ID}")
    
    # Extract schema for each table
    schemas = {}
    for table in tables:
        table_id = table.table_id
        logger.info(f"Processing schema for table {table_id}")
        
        try:
            # Use the imported function from schema_processor.py
            schema = get_table_schema(bq_client, PROJECT_ID, DATASET_ID, table_id)
            schemas[table_id] = schema
            
            # Save individual table schema
            table_schema_json = json.dumps(schema, indent=2)
            upload_to_gcs(BUCKET_NAME, f"{SCHEMA_PATH}/tables/{table_id}_schema.json", table_schema_json)
            logger.info(f"Uploaded schema for {table_id}")
        except Exception as e:
            logger.error(f"Error processing table {table_id}: {str(e)}")
    
    # Format schemas for prompt using the imported function
    prompt_format = format_schema_for_prompt(schemas)
    upload_to_gcs(BUCKET_NAME, f"{SCHEMA_PATH}/prompt_schema.md", prompt_format)
    logger.info("Uploaded formatted schema for prompts")
    
    # Save raw schema data
    all_schemas_json = json.dumps(schemas, indent=2)
    upload_to_gcs(BUCKET_NAME, f"{SCHEMA_PATH}/all_schemas.json", all_schemas_json)
    logger.info("Uploaded complete schema data")
    
    return f"gs://{BUCKET_NAME}/{SCHEMA_PATH}/prompt_schema.md"

def validate_schema_output(**kwargs):
    """
    Validates that the schema files were properly created
    """
    from google.cloud import storage
    import logging
    
    logger = logging.getLogger(__name__)
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    
    # Check for required files
    required_files = [
        f"{SCHEMA_PATH}/prompt_schema.md",
        f"{SCHEMA_PATH}/all_schemas.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        blob = bucket.blob(file_path)
        if not blob.exists():
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"Missing schema files: {missing_files}")
        raise ValueError(f"Schema extraction failed. Missing files: {missing_files}")
    
    logger.info("Schema validation successful")
    return True

# Define the DAG
dag = DAG(
    'extract_bigquery_schema',
    default_args=default_args,
    description='Extract schema from BigQuery for NL to SQL prompts',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=['nlsql', 'schema'],
)

# Task 1: Get dataset info
get_dataset_info = BigQueryGetDatasetOperator(
    task_id='get_dataset_info',
    dataset_id=DATASET_ID,
    project_id=PROJECT_ID,
    dag=dag
)

# Task 2: Extract and process schemas using our schema_processor functionality
process_schemas = PythonOperator(
    task_id='process_schemas',
    python_callable=extract_and_process_schemas,
    provide_context=True,
    dag=dag
)

# Task 3: Validate schema output
validate_schemas = PythonOperator(
    task_id='validate_schemas',
    python_callable=validate_schema_output,
    provide_context=True,
    dag=dag
)


send_slack_notification = SlackWebhookOperator(
    task_id='send_slack_notification',
    slack_webhook_conn_id='slack_webhook',  # Use this instead of http_conn_id
    message="✅ Airflow DAG `extract_bigquery_schema` completed successfully!",
    channel="#airflow-notifications",
    username="airflow-bot",
    dag=dag
)

# Set task dependencies
get_dataset_info >> process_schemas >> validate_schemas >> send_slack_notification