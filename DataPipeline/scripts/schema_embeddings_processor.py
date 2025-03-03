import json
import chromadb
import shutil
import os
from google.cloud import bigquery, storage
from langchain_google_vertexai import VertexAIEmbeddings

# Configuration Parameters
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
BUCKET_NAME = "bigquery-embeddings-store"
VERTEX_MODEL = "textembedding-gecko@003"
CHROMA_PATH = "/tmp/chromadb_store"
GCS_CHROMA_PATH = f"{DATASET_ID}/chromadb_store.zip"

# Initialize Vertex AI Embeddings
embedding_model = VertexAIEmbeddings(model=VERTEX_MODEL)

def extract_schema():
    client = bigquery.Client(project=PROJECT_ID)
    dataset_ref = client.dataset(DATASET_ID)
    tables = client.list_tables(dataset_ref)
    
    schema_data = []
    for table in tables:
        table_ref = dataset_ref.table(table.table_id)
        table_schema = client.get_table(table_ref).schema
        schema_text = " ".join([f"{field.name}: {field.field_type}" for field in table_schema])
        schema_data.append({"id": table.table_id, "text": schema_text})
    
    return schema_data

def create_embeddings():
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = chroma_client.get_or_create_collection(name=DATASET_ID)
    
    schema_data = extract_schema()
    texts = [item["text"] for item in schema_data]
    embeddings = embedding_model.embed_documents(texts)
    
    for idx, item in enumerate(schema_data):
        collection.add(ids=[item["id"]], embeddings=[embeddings[idx]], metadatas=[{"text": item["text"]}])

def save_chromadb_to_gcs():
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(GCS_CHROMA_PATH)
    
    shutil.make_archive("/tmp/chromadb_store", 'zip', CHROMA_PATH)
    blob.upload_from_filename("/tmp/chromadb_store.zip")
