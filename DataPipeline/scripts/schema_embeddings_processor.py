import os
import json
import numpy as np
import shutil
from google.cloud import bigquery, storage
from langchain_google_vertexai import VertexAIEmbeddings

# Configuration Parameters
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
VERTEX_MODEL = "textembedding-gecko@003"
BUCKET_NAME = "bigquery-embeddings-store"
EMBEDDINGS_FILE = "schema_embeddings.json"
LOCAL_EMBEDDINGS_PATH = f"/tmp/{EMBEDDINGS_FILE}"

# Initialize Vertex AI Embeddings
embedding_model = VertexAIEmbeddings(model=VERTEX_MODEL)
gcs_client = storage.Client()

def extract_schema():
    """Extract schema details with rich semantic descriptions."""
    client = bigquery.Client(project=PROJECT_ID)
    dataset_ref = client.dataset(DATASET_ID)
    tables = client.list_tables(dataset_ref)

    schema_data = []
    for table in tables:
        table_ref = dataset_ref.table(table.table_id)
        table_obj = client.get_table(table_ref)
        table_schema = table_obj.schema

        # Get table description if available
        table_desc = table_obj.description or table.table_id

        for field in table_schema:
            # Create a rich semantic description for each column
            field_desc = field.description or ""
            semantic_text = (
                f"This column represents {field.name} in the {table.table_id} table. "
                f"It stores {field_desc if field_desc else field.name} "
                f"with data type {field.field_type}. "
                f"The {table.table_id} table {table_desc}."
            )
            
            schema_data.append({
                "table": table.table_id,
                "column": field.name,
                "semantic_text": semantic_text
            })
    
    return schema_data

def generate_schema_embeddings():
    """Generate embeddings and store them in a JSON file."""
    schema_data = extract_schema()
    schema_texts = [item["semantic_text"] for item in schema_data]

    # Create embeddings for semantic descriptions
    schema_embeddings = embedding_model.embed_documents(schema_texts)

    schema_dict = {}
    for idx, item in enumerate(schema_data):
        key = f"{item['table']}:{item['column']}"
        schema_dict[key] = {
            'embedding': schema_embeddings[idx],
            'semantic_text': item['semantic_text']
        }
    
    #return schema_dict
    # Store embeddings in a JSON file
    # with open(LOCAL_EMBEDDINGS_PATH, "w") as f:
    #     json.dump(schema_dict, f)

    # print(f"✅ Schema embeddings stored locally at {LOCAL_EMBEDDINGS_PATH}")


def upload_embeddings_to_gcs():
    """Upload the embeddings JSON file to Google Cloud Storage."""
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(EMBEDDINGS_FILE)
    blob.upload_from_filename(LOCAL_EMBEDDINGS_PATH)
    print(f"✅ Embeddings file uploaded to GCS: gs://{BUCKET_NAME}/{EMBEDDINGS_FILE}")

def generate_and_store_embeddings():
    """
    Orchestrates the process of generating and storing embeddings.
    This function can be used for testing or manual runs.
    """
    try:
        print("🔄 Starting embeddings generation process...")
        
        # Step 1: Generate embeddings and store locally
        generate_schema_embeddings()
        
        # Step 2: Upload to GCS
        upload_embeddings_to_gcs()
        
        print("✅ Embeddings generation and storage process completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error in embeddings generation process: {str(e)}")
        return False

if __name__ == "__main__":
    # Run the process
    generate_and_store_embeddings()