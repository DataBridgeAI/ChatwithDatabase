
from airflow import DAG
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import tarfile
from google.cloud import bigquery, storage
import chromadb
import os
from sentence_transformers import SentenceTransformer
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.models import Variable
from feedback_processing import (
    extract_feedback_from_bigquery,
    generate_embeddings,
    archive_and_upload_chromadb
)
# Define constants
GCP_PROJECT_ID = "chatwithdata-451800"
BQ_DATASET = "Feedback_Dataset"
BQ_TABLE = "user_feedback"
GCS_BUCKET = "feedback-questions-embeddings-store"
CSV_FILE_PATH = "/tmp/feedback_data.csv"
PROCESSED_CSV_PATH = "/tmp/processed_feedback.csv"
CHROMADB_PATH = "/tmp/chroma_db"
CHROMADB_ARCHIVE_PATH = "/tmp/chroma_db.tar.gz"
EMBEDDINGS_COLLECTION_NAME = "feedback_questions"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path=CHROMADB_PATH)
collection = chroma_client.get_or_create_collection(EMBEDDINGS_COLLECTION_NAME)

# Initialize Sentence Transformer model
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

# Define default args
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


# Define DAG
with DAG(
    "feedback_embeddings_dag",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
) as dag:
    
    extract_feedback = PythonOperator(
        task_id="extract_feedback",
        python_callable=extract_feedback_from_bigquery
    )
    
    create_embeddings = PythonOperator(
        task_id="create_embeddings",
        python_callable=generate_embeddings
    )
    
    archive_chromadb = PythonOperator(
        task_id="archive_chromadb",
        python_callable=archive_and_upload_chromadb
    )
    
    upload_csv_to_gcs = LocalFilesystemToGCSOperator(
        task_id="upload_csv_to_gcs",
        src=PROCESSED_CSV_PATH,
        dst="processed_feedback.csv",
        bucket=GCS_BUCKET
    )
    
    upload_chromadb_to_gcs = LocalFilesystemToGCSOperator(
        task_id="upload_chromadb_to_gcs",
        src=CHROMADB_ARCHIVE_PATH,
        dst="chroma_db.tar.gz",
        bucket=GCS_BUCKET
    )
    
    send_slack_notification = SlackWebhookOperator(
    task_id='send_slack_notification',
    slack_webhook_conn_id='slack_webhook',  # Use this instead of http_conn_id
    message="✅ Airflow DAG `feedback_embeddings_dag` completed successfully!",
    channel="#airflow-notifications",
    username="airflow-bot",
    dag=dag
    )

    extract_feedback >> create_embeddings >> archive_chromadb >> [upload_csv_to_gcs, upload_chromadb_to_gcs] >> send_slack_notification
