# # Task dependencies
# extract_schema_task >> generate_embeddings_task
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import json
import chromadb
from langchain_google_vertexai import VertexAIEmbeddings
from google.cloud import bigquery, storage
import shutil
import os
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.models import Variable
from schema_embeddings_processor import create_embeddings, save_chromadb_to_gcs

# Configuration Parameters
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
BUCKET_NAME = "bigquery-embeddings-store"
VERTEX_MODEL = "textembedding-gecko@003"
CHROMA_PATH = "/tmp/chromadb_store"
GCS_CHROMA_PATH = f"{DATASET_ID}/chromadb_store.zip"

# Initialize Vertex AI Embeddings
embedding_model = VertexAIEmbeddings(model=VERTEX_MODEL)


# Defining DAG
with DAG(
    dag_id="schema_embeddings_dag",
    schedule_interval=None,  # Set as needed
    start_date=datetime(2024, 3, 1),
    catchup=False,
) as dag:
    
    create_embeddings_task = PythonOperator(
        task_id="create_embeddings",
        python_callable=create_embeddings
    )
    
    save_chromadb_task = PythonOperator(
        task_id="save_chromadb_to_gcs",
        python_callable=save_chromadb_to_gcs
    )

    send_slack_notification = SlackWebhookOperator(
    task_id='send_slack_notification',
    slack_webhook_conn_id='slack_webhook',  # Use this instead of http_conn_id
    message="✅ Airflow DAG `schema_embeddings_dag` completed successfully!",
    channel="#airflow-notifications",
    username="airflow-bot",
    dag=dag
    )

    
    create_embeddings_task >> save_chromadb_task >> send_slack_notification
