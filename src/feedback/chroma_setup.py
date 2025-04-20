import os
import zipfile
from google.cloud import storage

# Constants
BUCKET_NAME = "feedback-questions-embeddings-store"
ZIP_BLOB_NAME = "chroma_db/persistentdb.zip"
LOCAL_ZIP_PATH = "retrieved_chroma.zip"
LOCAL_EXTRACT_PATH = "./retrieved_chroma/"

# Initialize GCS client
storage_client = storage.Client()

def download_and_extract_chromadb():
    """Downloads and extracts the ChromaDB zip from GCS if not already extracted."""
    if os.path.exists(LOCAL_EXTRACT_PATH):
        print("ChromaDB already extracted, skipping download.")
        return

    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(ZIP_BLOB_NAME)

    # Download the zip file
    blob.download_to_filename(LOCAL_ZIP_PATH)
    print(f"Downloaded {ZIP_BLOB_NAME} to {LOCAL_ZIP_PATH}")

    # Extract the zip file
    with zipfile.ZipFile(LOCAL_ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(LOCAL_EXTRACT_PATH)
    print(f"Extracted ChromaDB store to {LOCAL_EXTRACT_PATH}")