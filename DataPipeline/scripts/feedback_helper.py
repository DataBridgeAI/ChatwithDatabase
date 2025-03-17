import os
import shutil
from google.cloud import bigquery, storage
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

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

# Initialize clients
storage_client = storage.Client()
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

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

def generate_query_embeddings():
    """Generate embeddings for fetched queries and store them locally."""
    if not os.path.exists("queries.txt"):
        print("No queries found. Skipping embedding generation.")
        return

    chroma_client = PersistentClient(path=LOCAL_PERSIST_PATH)
    collection = chroma_client.get_or_create_collection(name="queries")

    with open("queries.txt", "r") as f:
        for line in f:
            user_query, generated_sql, feedback = line.strip().split("||")
            embedding = embedding_model.encode(user_query)
            collection.add(
                documents=[user_query],
                embeddings=[embedding],
                metadatas=[{"generated_sql": generated_sql, "feedback": feedback}],
                ids=[str(hash(user_query))]
            )

def fetch_user_queries():
    """Fetch user queries, generated SQL, and feedback from BigQuery"""
    client = bigquery.Client(project=BIGQUERY_PROJECT_ID)
    query = f"""
    SELECT user_question, generated_sql, feedback
    FROM `{BIGQUERY_PROJECT_ID}.{BIGQUERY_DATASET}.{BIGQUERY_TABLE}`
    WHERE feedback = '1'
    """
    results = client.query(query).result()
    queries = [(row.user_question, row.generated_sql, row.feedback) for row in results]

    if queries:
        with open("queries.txt", "w") as f:
            for query in queries:
                f.write(f"{query[0]}||{query[1]}||{query[2]}\n")
    
    return queries
    # return [(row.user_question, row.generated_sql, row.feedback) for row in results]


def store_embeddings_gcs(user_query, embedding, generated_sql, feedback):
    """Store embedding and metadata in ChromaDB and then upload to GCS"""
    chroma_client = PersistentClient(path=LOCAL_PERSIST_PATH)
    collection = chroma_client.get_or_create_collection(name="queries")
    collection.add(
        documents=[user_query],
        embeddings=[embedding],
        metadatas=[{"generated_sql": generated_sql, "feedback": feedback}],
        ids=[str(hash(user_query))]
    )


