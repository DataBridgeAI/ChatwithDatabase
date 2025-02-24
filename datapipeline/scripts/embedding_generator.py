from google.cloud import bigquery, storage
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os

# Google Cloud configurations
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "Songs"
BUCKET_NAME = "schema-embeddings-db"

# Initialize clients
bq_client = bigquery.Client(project=PROJECT_ID)
storage_client = storage.Client()

# Load embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def get_schema():
    """Fetches schema details from BigQuery."""
    query = f"""
    SELECT table_name, column_name, data_type 
    FROM `{PROJECT_ID}.{DATASET_ID}.INFORMATION_SCHEMA.COLUMNS`
    """
    schema_df = bq_client.query(query).to_dataframe()
    schema_info = [f"Table: {row['table_name']}, Column: {row['column_name']} ({row['data_type']})" 
                   for _, row in schema_df.iterrows()]
    return schema_info

def generate_schema_embeddings():
    """Generates embeddings for BigQuery schema and uploads to GCS."""
    schema_info = get_schema()
    embeddings = embedding_model.encode(schema_info, convert_to_numpy=True)

    # Create FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    # Save locally
    schema_texts_path = "schema_texts.pkl"
    faiss_index_path = "schema_index.faiss"

    with open(schema_texts_path, "wb") as f:
        pickle.dump(schema_info, f)
    with open(faiss_index_path, "wb") as f:
        pickle.dump(index, f)

    # Upload to GCS
    bucket = storage_client.bucket(BUCKET_NAME)
    
    for local_path, gcs_path in [(schema_texts_path, "schema/schema_texts.pkl"), 
                                 (faiss_index_path, "schema/schema_index.faiss")]:
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_path)
        os.remove(local_path)

    print("Schema embeddings updated and uploaded to GCS.")

if __name__ == "__main__":
    generate_schema_embeddings()
