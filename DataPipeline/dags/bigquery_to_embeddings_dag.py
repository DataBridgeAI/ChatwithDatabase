from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryHook
from airflow.providers.google.cloud.operators.gcs import GCSToLocalFilesystemOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from google.cloud import bigquery, storage
import os

# Define constants
GCP_PROJECT_ID = "chatwithdata-451800"
BQ_DATASET = "Feedback_Dataset"
BQ_TABLE = "user_feedback"
GCS_BUCKET = "feeback-questions-embeddings-store"
CSV_FILE_PATH = "/tmp/feedback_data.csv"
EMBEDDINGS_FILE_PATH = "/tmp/question_embeddings.npy"
PROCESSED_CSV_PATH = "/tmp/processed_feedback.csv"

# Define default args
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define function to extract BigQuery data
def extract_feedback_from_bigquery():
    client = bigquery.Client(project=GCP_PROJECT_ID)
    query = f"""
    SELECT user_question, generated_sql, corrected_sql 
    FROM `{GCP_PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}`
    WHERE feedback = 'thumbs_down';
    """
    
    df = client.query(query).to_dataframe()
    df.to_csv(CSV_FILE_PATH, index=False)
    print(f"Extracted {len(df)} rows from BigQuery and saved to {CSV_FILE_PATH}")

# Define function to generate embeddings
def generate_embeddings():
    df = pd.read_csv(CSV_FILE_PATH)
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    df["question_embedding"] = df["user_question"].apply(lambda q: model.encode(q).tolist())
    embeddings = np.vstack(df["question_embedding"].values)
    
    # Save embeddings as NumPy array
    np.save(EMBEDDINGS_FILE_PATH, embeddings)
    
    # Save updated DataFrame
    df.to_csv(PROCESSED_CSV_PATH, index=False)
    print(f"Saved embeddings and processed data.")

# Define DAG
with DAG(
    "bigquery_to_embeddings_dag",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
) as dag:

    # Task 1: Extract feedback from BigQuery and save as CSV
    extract_feedback = PythonOperator(
        task_id="extract_feedback",
        python_callable=extract_feedback_from_bigquery
    )

    # Task 2: Generate embeddings and save to file
    create_embeddings = PythonOperator(
        task_id="create_embeddings",
        python_callable=generate_embeddings
    )

    # Task 3: Upload processed CSV to GCS
    upload_csv_to_gcs = LocalFilesystemToGCSOperator(
        task_id="upload_csv_to_gcs",
        src=PROCESSED_CSV_PATH,
        dst="processed_feedback.csv",
        bucket=GCS_BUCKET
    )

    # Task 4: Upload embeddings file to GCS
    upload_embeddings_to_gcs = LocalFilesystemToGCSOperator(
        task_id="upload_embeddings_to_gcs",
        src=EMBEDDINGS_FILE_PATH,
        dst="question_embeddings.npy",
        bucket=GCS_BUCKET
    )

    # Define DAG workflow
    extract_feedback >> create_embeddings >> [upload_csv_to_gcs, upload_embeddings_to_gcs]
