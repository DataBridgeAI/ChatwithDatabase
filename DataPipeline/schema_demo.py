import json
import os
import shutil
import numpy as np
import chromadb
from google.cloud import bigquery, storage
from langchain_google_vertexai import VertexAIEmbeddings
from datetime import timedelta, datetime, date

# GCP Configuration
PROJECT_ID = "chatwithdata-451800"
BUCKET_NAME = "bigquery-embeddings-store"
VERTEX_MODEL = "textembedding-gecko@003"
CHROMADB_PATH = "/home/airflow/gcs/data/chroma_db"  # Cloud Composer stores files in /home/airflow/gcs/data

# Initialize clients
bq_client = bigquery.Client()
storage_client = storage.Client()
embedding_model = VertexAIEmbeddings(model_name=VERTEX_MODEL)

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

            # Store in ChromaDB
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

    # Zip ChromaDB directory
    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', CHROMADB_PATH)

    # Upload to GCS
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob("chroma_db_backup.zip")
    blob.upload_from_filename(zip_path)

    print("ChromaDB backup uploaded to GCS successfully!")


# Run the functions in sequence
if __name__ == "__main__":
    print("Starting the process...")

    # Step 1: Generate embeddings and store them in ChromaDB
    generate_and_store_embeddings()

    # Step 2: Backup ChromaDB to Google Cloud Storage
    backup_chromadb_to_gcs()

    print("Process completed.")
