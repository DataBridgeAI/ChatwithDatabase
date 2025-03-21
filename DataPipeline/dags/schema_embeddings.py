from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.models import Variable

# Import the processing functions
from scripts.schema_embeddings_processor import (
    generate_schema_embeddings,
    upload_embeddings_to_gcs,
    generate_and_store_embeddings
)

# Configuration (matching processor.py)
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
BUCKET_NAME = "bigquery-embeddings-store"
VERTEX_MODEL = "textembedding-gecko@003"

# Define the DAG
with DAG(
    dag_id="schema_embeddings_dag",
    schedule_interval=None,  # Set as needed
    start_date=datetime(2025, 3, 1),
    catchup=False,
    tags=['schema', 'embeddings']
) as dag:
    
    # Task 1: Generate embeddings and store locally
    generate_embeddings_task = PythonOperator(
        task_id="generate_embeddings",
        python_callable=generate_schema_embeddings,
        dag=dag
    )
    
    # Task 2: Upload embeddings to GCS
    upload_to_gcs_task = PythonOperator(
        task_id="upload_to_gcs",
        python_callable=upload_embeddings_to_gcs,
        dag=dag
    )

    # Task 3: Send Slack notification
    send_slack_notification = SlackWebhookOperator(
        task_id='send_slack_notification',
        slack_webhook_conn_id='slack_webhook',
        message="✅ Schema embeddings generation and upload completed successfully!",
        channel="#airflow-notifications",
        username="airflow-bot",
        dag=dag
    )

    # Define task dependencies
    generate_embeddings_task >> upload_to_gcs_task >> send_slack_notification
