import os
import shutil
import zipfile
from google.cloud import bigquery, storage
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
import threading

# Configurations
GCS_BUCKET_NAME = "feedback-questions-embeddings-store"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

BIGQUERY_PROJECT_ID = "chatwithdata-451800"
BIGQUERY_DATASET = "Feedback_Dataset"
BIGQUERY_TABLE = "user_feedback"

BUCKET_NAME = "feedback-questions-embeddings-store"
GCS_PERSIST_PATH = "chroma_db/"
LOCAL_PERSIST_PATH = "./persistentdb/"
ZIP_FILE_PATH = "./persistentdb.zip"
GCS_ZIP_PATH = "chroma_db/persistentdb.zip"

# Global variables
_model_lock = threading.Lock()
_model = None

# Initialize clients
storage_client = storage.Client()

def get_embedding_model():
    """Get or initialize the embedding model in a thread-safe way"""
    global _model
    with _model_lock:
        if _model is None:
            _model = SentenceTransformer(EMBEDDING_MODEL)
        return _model

# Ensure the local directory exists
os.makedirs(LOCAL_PERSIST_PATH, exist_ok=True)

def zip_directory():
    """Zip the ChromaDB directory."""
    shutil.make_archive(ZIP_FILE_PATH.replace(".zip", ""), 'zip', LOCAL_PERSIST_PATH)
    print(f"Zipped directory {LOCAL_PERSIST_PATH} to {ZIP_FILE_PATH}")

def upload_zip_to_gcs():
    """Upload zipped embeddings to Google Cloud Storage."""
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(GCS_ZIP_PATH)
    blob.upload_from_filename(ZIP_FILE_PATH)
    print(f"Uploaded {ZIP_FILE_PATH} to gs://{GCS_BUCKET_NAME}/{GCS_ZIP_PATH}")


def fetch_user_queries(hours=24):
    """Fetch user queries from the last specified hours"""
    client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
    query = f"""
    SELECT user_question, generated_sql, feedback
    FROM `{BIGQUERY_PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
    WHERE feedback = '1'
    AND TIMESTAMP_ADD(timestamp, INTERVAL -{hours} HOUR) <= CURRENT_TIMESTAMP()
    """
    results = client.query(query).result()
    queries = [(row.user_question, row.generated_sql, row.feedback) for row in results]
    return queries

def download_existing_embeddings():
    """Download and extract existing embeddings from GCS"""
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(GCS_ZIP_PATH)
    
    if not os.path.exists(LOCAL_PERSIST_PATH):
        os.makedirs(LOCAL_PERSIST_PATH)
    
    # Download existing zip if it exists
    try:
        blob.download_to_filename(ZIP_FILE_PATH)
        with zipfile.ZipFile(ZIP_FILE_PATH, 'r') as zip_ref:
            zip_ref.extractall(LOCAL_PERSIST_PATH)
        print("Downloaded and extracted existing embeddings")
    except Exception as e:
        print(f"No existing embeddings found or error: {e}")

def update_query_embeddings(queries):
    """Update embeddings with new queries from the last 24 hours"""
    if not queries:
        print("No new queries found. Skipping embedding generation.")
        return

    # First download existing embeddings
    download_existing_embeddings()

    # Initialize model only when needed
    model = get_embedding_model()

    # Initialize ChromaDB client
    chroma_client = PersistentClient(path=LOCAL_PERSIST_PATH)
    collection = chroma_client.get_or_create_collection(name="queries")

    # Add new embeddings
    for query_data in queries:
        user_query, generated_sql, feedback = query_data
        query_id = str(hash(user_query))
        
        # Check if query already exists
        existing_results = collection.get(
            ids=[query_id],
            include=['metadatas']
        )
        
        if not existing_results['ids']:
            embedding = model.encode(user_query)
            collection.add(
                documents=[user_query],
                embeddings=[embedding],
                metadatas=[{"generated_sql": generated_sql, "feedback": feedback}],
                ids=[query_id]
            )
            print(f"Added new embedding for query: {user_query[:50]}...")

