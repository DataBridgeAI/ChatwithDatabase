import json
import os
import shutil
import numpy as np
import chromadb
from google.cloud import bigquery, storage
from langchain_google_vertexai import VertexAIEmbeddings
from datetime import timedelta, datetime, date
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.cloud_storage import GCSUploadFileOperator

# GCP Configuration
PROJECT_ID = "chatwithdata-451800"
BUCKET_NAME = "bigquery-embeddings-store"
VERTEX_MODEL = "textembedding-gecko@003"
CHROMADB_PATH = "/home/airflow/gcs/data/chroma_db"  # Cloud Composer stores files in /home/airflow/gcs/data
# Use GCS path if you'd like to store ChromaDB in GCS directly:
# CHROMADB_PATH = "gs://<bucket_name>/chroma_db"

# Initialize clients
bq_client = bigquery.Client()
storage_client = storage.Client()
embedding_model = VertexAIEmbeddings(model_name=VERTEX_MODEL)

# Airflow DAG setup
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 3, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'bigquery_schema_to_chromadb',
    default_args=default_args,
    description='Extract schema, generate embeddings, store in ChromaDB & backup to GCS',
    schedule_interval='@daily',  # Runs every day
    catchup=False,
)

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMADB_PATH)
collection = chroma_client.get_or_create_collection(name="bigquery_schemas")

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle complex types."""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

def extract_schema():
    """Extract schema details from all datasets & tables in BigQuery."""
    schema_info = {}
    datasets = list(bq_client.list_datasets(PROJECT_ID))
    if not datasets:
        print("No datasets found.")
        return schema_info

    for dataset in datasets:
        dataset_id = dataset.dataset_id
        schema_info[dataset_id] = {}
        tables = bq_client.list_tables(f"{PROJECT_ID}.{dataset_id}")
        for table in tables:
            table_id = table.table_id
            schema_info[dataset_id][table_id] = {}

            table_ref = bq_client.get_table(f"{PROJECT_ID}.{dataset_id}.{table_id}")
            for field in table_ref.schema:
                column_data = {"type": field.field_type}
                if field.field_type in ["INTEGER", "FLOAT", "NUMERIC", "DATE", "TIMESTAMP"]:
                    query = f"SELECT MIN({field.name}) AS min_value, MAX({field.name}) AS max_value FROM `{PROJECT_ID}.{dataset_id}.{table_id}`"
                    df = bq_client.query(query).to_dataframe()
                    column_data["min_value"] = df["min_value"].iloc[0] if not df.empty else None
                    column_data["max_value"] = df["max_value"].iloc[0] if not df.empty else None
                elif field.field_type == "STRING":
                    query = f"SELECT DISTINCT {field.name} FROM `{PROJECT_ID}.{dataset_id}.{table_id}` LIMIT 100"
                    df = bq_client.query(query).to_dataframe()
                    column_data["unique_values"] = df[field.name].tolist()
                schema_info[dataset_id][table_id][field.name] = column_data

    return schema_info

def generate_and_store_embeddings():
    """Generate embeddings & store in ChromaDB."""
    schema_info = extract_schema()
    if not schema_info:
        print("No schema extracted.")
        return

    for dataset_id, tables in schema_info.items():
        for table_id, schema in tables.items():
            schema_text = json.dumps(schema, indent=2, cls=CustomJSONEncoder)
            embedding = embedding_model.embed_documents([schema_text])[0]
            doc_id = f"{dataset_id}.{table_id}"
            collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[{"dataset": dataset_id, "table": table_id}]
            )
            print(f"Stored embedding for {doc_id} in ChromaDB")

def backup_chromadb_to_gcs():
    """Compress & upload ChromaDB database to GCS."""
    zip_path = "/home/airflow/gcs/data/chroma_db_backup.zip"
    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', CHROMADB_PATH)

    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob("chroma_db_backup.zip")
    blob.upload_from_filename(zip_path)
    print("ChromaDB backup uploaded to GCS successfully!")

# Define Airflow tasks
extract_schema_task = PythonOperator(
    task_id='extract_schema_task',
    python_callable=extract_schema,
    dag=dag,
)

generate_embeddings_task = PythonOperator(
    task_id='generate_embeddings_task',
    python_callable=generate_and_store_embeddings,
    dag=dag,
)

backup_chromadb_task = PythonOperator(
    task_id='backup_chromadb_task',
    python_callable=backup_chromadb_to_gcs,
    dag=dag,
)

# Task dependencies
extract_schema_task >> generate_embeddings_task >> backup_chromadb_task
