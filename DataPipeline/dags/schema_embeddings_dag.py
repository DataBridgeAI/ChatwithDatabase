# dags/schema_embeddings_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from google.cloud import bigquery
from airflow.models import Variable
from scripts.schema_embedding import extract_schema, create_embeddings, save_chromadb_to_gcs

# Default args for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Configuration Variables
PROJECT_ID = Variable.get("gcp_project_id")
DATASET_ID = Variable.get("bigquery_dataset_id")
BUCKET_NAME = Variable.get("gcs_bucket")
CHROMA_PATH = "/tmp/chromadb_store"

def extract_and_process_embeddings(**kwargs):
    """
    Extract schema from BigQuery, create embeddings, and save to GCS
    """
    try:
        # Initialize BigQuery client
        bq_client = bigquery.Client(project=PROJECT_ID)
        logger = kwargs['logger']
        logger.info(f"Extracting schema for dataset {DATASET_ID}")
        
        # Extract schema data
        schema_data = extract_schema(bq_client, DATASET_ID)
        
        # Create embeddings for schema data
        create_embeddings(schema_data)
        
        # Save Chroma database to GCS
        save_chromadb_to_gcs()
    except Exception as e:
        logger.error(f"Error processing schema embedding: {str(e)}")
        raise

# Define the DAG
dag = DAG(
    'schema_embeddings_dag',
    default_args=default_args,
    description='Create schema embeddings and save to GCS',
    schedule_interval=None,  # Set schedule as needed
    start_date=datetime(2024, 3, 1),
    catchup=False,
    tags=['schema', 'embedding', 'nlp']
)

# Task to extract schema, create embeddings, and save to GCS
process_schema_embeddings = PythonOperator(
    task_id="process_schema_embeddings",
    python_callable=extract_and_process_embeddings,
    provide_context=True,
    dag=dag
)
