# # dags/extract_bigquery_schema.py
# from datetime import datetime, timedelta
# from airflow import DAG
# from airflow.providers.google.cloud.operators.bigquery import BigQueryGetDatasetOperator
# from airflow.providers.google.cloud.transfers.bigquery_to_gcs import BigQueryToGCSOperator
# from airflow.operators.python import PythonOperator
# from airflow.utils.dates import days_ago
# import json
# import os

# # Define default args
# default_args = {
#     'owner': 'airflow',
#     'depends_on_past': False,
#     'email_on_failure': False,
#     'email_on_retry': False,
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5),
# }

# # Config variables
# PROJECT_ID = '{{ var.value.gcp_project_id }}'
# DATASET_ID = '{{ var.value.bigquery_dataset_id }}'
# BUCKET_NAME = '{{ var.value.gcs_bucket }}'
# SCHEMA_PATH = 'schema_data'

# def process_schema_for_prompt(**kwargs):
#     """Process schema data from BigQuery and format it for OpenAI prompt"""
#     import pandas as pd
#     from google.cloud import storage
    
#     # Get schemas from task instance
#     ti = kwargs['ti']
#     dataset_info = ti.xcom_pull(task_ids='get_dataset_info')
    
#     # Process the schema information into a structured format for prompting
#     tables = dataset_info.get('tables', [])
#     schema_data = {}
    
#     # Format schema data
#     for table in tables:
#         table_id = table['tableReference']['tableId']
#         table_schema_file = f"gs://{BUCKET_NAME}/{SCHEMA_PATH}/{table_id}_schema.json"
        
#         # Read schema file from GCS
#         storage_client = storage.Client()
#         bucket = storage_client.bucket(BUCKET_NAME)
#         blob = bucket.blob(f"{SCHEMA_PATH}/{table_id}_schema.json")
#         schema_text = blob.download_as_text()
#         schema_json = json.loads(schema_text)
        
#         # Format for prompt template
#         columns = []
#         for field in schema_json.get('schema', {}).get('fields', []):
#             column_info = {
#                 'name': field.get('name'),
#                 'type': field.get('type'),
#                 'mode': field.get('mode', 'NULLABLE'),
#                 'description': field.get('description', '')
#             }
#             columns.append(column_info)
        
#         schema_data[table_id] = {
#             'columns': columns,
#             'description': schema_json.get('description', ''),
#             'numRows': schema_json.get('numRows', 0)
#         }
    
#     # Save the formatted schema data
#     prompt_schema = json.dumps(schema_data, indent=2)
#     output_blob = bucket.blob(f"{SCHEMA_PATH}/prompt_schema.json")
#     output_blob.upload_from_string(prompt_schema)
    
#     # Return the path to the schema file
#     return f"gs://{BUCKET_NAME}/{SCHEMA_PATH}/prompt_schema.json"

# # Define the DAG
# dag = DAG(
#     'extract_bigquery_schema',
#     default_args=default_args,
#     description='Extract schema from BigQuery for NL to SQL prompts',
#     schedule_interval=timedelta(days=1),
#     start_date=days_ago(1),
#     tags=['nlsql', 'schema'],
# )

# # Task 1: Get dataset info including tables
# get_dataset_info = BigQueryGetDatasetOperator(
#     task_id='get_dataset_info',
#     dataset_id=DATASET_ID,
#     project_id=PROJECT_ID,
#     dag=dag
# )

# # Task 2: For each table, export schema to GCS
# export_table_schemas = BigQueryToGCSOperator(
#     task_id='export_table_schemas',
#     source_project_dataset_table=f"{PROJECT_ID}.{DATASET_ID}",
#     destination_cloud_storage_uris=[f"gs://{BUCKET_NAME}/{SCHEMA_PATH}/{{table}}_schema.json"],
#     export_format='AVRO',
#     dag=dag
# )

# # Task 3: Process schema data for prompt engineering
# process_schema = PythonOperator(
#     task_id='process_schema',
#     python_callable=process_schema_for_prompt,
#     provide_context=True,
#     dag=dag
# )

# # Set task dependencies
# get_dataset_info >> export_table_schemas >> process_schema

# dags/extract_bigquery_schema.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryGetDatasetOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.dates import days_ago
import os
import sys
import json
import logging
from airflow.models import Variable

# Add scripts directory to path to import schema_processor
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../scripts'))
from scripts.schema_processor import get_table_schema, format_schema_for_prompt, upload_to_gcs

# Define default args
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Config variables
# PROJECT_ID = '{{ var.value.gcp_project_id }}'
# DATASET_ID = '{{ var.value.bigquery_dataset_id }}'
# BUCKET_NAME = '{{ var.value.gcs_bucket }}'
PROJECT_ID = Variable.get("gcp_project_id")
DATASET_ID =  Variable.get("bigquery_dataset_id")
BUCKET_NAME = Variable.get("gcs_bucket")
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

# Set task dependencies
get_dataset_info >> process_schemas >> validate_schemas