import os
import json
import numpy as np
import shutil
from google.cloud import bigquery, storage
from sklearn.metrics.pairwise import cosine_similarity
# Constants
# DATASET_ID = "RetailDataset"
# BUCKET_NAME = "bigquery-embeddings-store"
# ZIP_BLOB_NAME = f"{DATASET_ID}/chromadb_store.zip"
# LOCAL_ZIP_PATH = "/tmp/chromadb_store.zip"
# LOCAL_EXTRACT_PATH = "/tmp/chromadb_store"
# CHROMA_PATH = "/tmp/chromadb_store"

# Configuration Parameters
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
VERTEX_MODEL = "textembedding-gecko@003"
BUCKET_NAME = "bigquery-embeddings-store"
EMBEDDINGS_FILE = "schema_embeddings.json"
LOCAL_EMBEDDINGS_PATH = f"/tmp/{EMBEDDINGS_FILE}"

# Initialize Vertex AI Embeddings
#embedding_model = VertexAIEmbeddings(model=VERTEX_MODEL)
gcs_client = storage.Client()

def download_embeddings_from_gcs():
    """Download the embeddings JSON file from GCS."""
    bucket = gcs_client.bucket(BUCKET_NAME)
    blob = bucket.blob(EMBEDDINGS_FILE)

    if not os.path.exists(LOCAL_EMBEDDINGS_PATH):
        blob.download_to_filename(LOCAL_EMBEDDINGS_PATH)
        #print(f"✅ Embeddings file downloaded from GCS to {LOCAL_EMBEDDINGS_PATH}")

def load_schema_embeddings():
    """Load schema embeddings from JSON file."""
    if not os.path.exists(LOCAL_EMBEDDINGS_PATH):
        #print("❌ No local embeddings file found. Downloading from GCS...")
        download_embeddings_from_gcs()

    if not os.path.exists(LOCAL_EMBEDDINGS_PATH):
        #print("❌ Error: Unable to load schema embeddings!")
        return {}

    with open(LOCAL_EMBEDDINGS_PATH, "r") as f:
        schema_embeddings = json.load(f)

    #print(f"✅ Loaded {len(schema_embeddings)} schema embeddings from JSON file.")
    return schema_embeddings

def download_and_load_embeddings():
    """
    Downloads embeddings from GCS and loads them into memory.
    Returns a dictionary of schema embeddings.
    """
    try:
        # First try to download if not exists locally
        if not os.path.exists(LOCAL_EMBEDDINGS_PATH):
            print("📥 Downloading embeddings from GCS...")
            download_embeddings_from_gcs()
        
        # Load the embeddings
        print("📂 Loading schema embeddings...")
        schema_embeddings = load_schema_embeddings()
        
        if not schema_embeddings:
            raise Exception("Failed to load schema embeddings")
            
        print(f"✅ Successfully loaded {len(schema_embeddings)} schema embeddings")
        return schema_embeddings
        
    except Exception as e:
        print(f"❌ Error in download_and_load_embeddings: {str(e)}")
        return None

def compare_embeddings(query_embedding: np.ndarray, schema_embeddings: dict, threshold: float = 0.7) -> bool:
    """
    Compares query embedding with schema embeddings.
    Returns True if query is relevant to schema.
    """
    try:
        max_similarity = 0.0
        
        # Compare with each schema embedding
        for schema_id, schema_data in schema_embeddings.items():
            schema_embedding = np.array(schema_data['embedding'])
            similarity = cosine_similarity(
                query_embedding.reshape(1, -1), 
                schema_embedding.reshape(1, -1)
            )[0][0]
            max_similarity = max(max_similarity, similarity)
            
            if max_similarity >= threshold:
                return True
                
        return False
        
    except Exception as e:
        print(f"❌ Error in compare_embeddings: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    # Load embeddings
    schema_embeddings = download_and_load_embeddings()
    
    if schema_embeddings:
        print("🔍 Schema embeddings loaded and ready for comparison")
        # You can now use these embeddings with compare_embeddings() function
        # when you have query embeddings to compare against

