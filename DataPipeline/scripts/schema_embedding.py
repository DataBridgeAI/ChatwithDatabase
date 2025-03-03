# scripts/schema_embedding_processor.py
import json
import chromadb
import shutil
from google.cloud import bigquery, storage
from langchain_google_vertexai import VertexAIEmbeddings
import logging
import tempfile
import os


# Configuration Parameters
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
BUCKET_NAME = "bigquery-embeddings-store"
VERTEX_MODEL = "textembedding-gecko@003"
CHROMA_PATH = "/tmp/chromadb_store"
GCS_CHROMA_PATH = f"{DATASET_ID}/chromadb_store.zip"

# Initialize Vertex AI Embeddings
embedding_model = VertexAIEmbeddings(model=VERTEX_MODEL)

logger = logging.getLogger("airflow.task")
logger.setLevel(logging.INFO)

def extract_schema(client, dataset_id):
    """
    Extract schema data from BigQuery tables
    """
    try:
        dataset_ref = client.dataset(dataset_id)
        tables = client.list_tables(dataset_ref)
        
        schema_data = []
        for table in tables:
            table_ref = dataset_ref.table(table.table_id)
            table_schema = client.get_table(table_ref).schema
            schema_text = " ".join([f"{field.name}: {field.field_type}" for field in table_schema])
            schema_data.append({"id": table.table_id, "text": schema_text})
        
        return schema_data
    except Exception as e:
        logger.error(f"Error extracting schema: {str(e)}")
        raise

def create_embeddings(schema_data):
    """
    Create embeddings for schema data using Vertex AI model
    """
    try:
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = chroma_client.get_or_create_collection(name=DATASET_ID)
        
        texts = [item["text"] for item in schema_data]
        embeddings = embedding_model.embed_documents(texts)
        
        for idx, item in enumerate(schema_data):
            collection.add(ids=[item["id"]], embeddings=[embeddings[idx]], metadatas=[{"text": item["text"]}])
        
        logger.info("Embeddings created successfully.")
    except Exception as e:
        logger.error(f"Error creating embeddings: {str(e)}")
        raise

# Dynamically set CHROMA_PATH based on the platform
if os.name == 'nt':  # For Windows
    CHROMA_PATH = os.path.join(tempfile.gettempdir(), "chromadb_store")
else:  # For Linux/Mac
    CHROMA_PATH = "/tmp/chromadb_store"

logger = logging.getLogger("airflow.task")
logger.setLevel(logging.INFO)

def save_chromadb_to_gcs():
    """
    Save the Chroma database to Google Cloud Storage
    """
    try:
        # Create a temporary directory using tempfile for cross-platform compatibility
        with tempfile.TemporaryDirectory() as tmpdir:
            chromadb_zip_path = os.path.join(tmpdir, "chromadb_store.zip")
            
            # Ensure CHROMA_PATH is set to the correct directory
            if not os.path.exists(CHROMA_PATH):
                raise FileNotFoundError(f"Chroma directory not found: {CHROMA_PATH}")
            
            # Create the zip archive in the temporary directory
            shutil.make_archive(chromadb_zip_path.replace('.zip', ''), 'zip', CHROMA_PATH)

            client = storage.Client()
            bucket = client.bucket(BUCKET_NAME)
            blob = bucket.blob(GCS_CHROMA_PATH)

            # Upload the zip file to GCS
            blob.upload_from_filename(chromadb_zip_path)
            
            logger.info(f"Chroma database saved to GCS at {GCS_CHROMA_PATH}")
    except Exception as e:
        logger.error(f"Error saving Chroma database to GCS: {str(e)}")
        raise