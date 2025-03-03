import pandas as pd
import tarfile
import os
from google.cloud import bigquery
import chromadb
from sentence_transformers import SentenceTransformer

# Constants
GCP_PROJECT_ID = "chatwithdata-451800"
BQ_DATASET = "Feedback_Dataset"
BQ_TABLE = "user_feedback"
CSV_FILE_PATH = "/tmp/feedback_data.csv"
PROCESSED_CSV_PATH = "/tmp/processed_feedback.csv"
CHROMADB_PATH = "/tmp/chroma_db"
CHROMADB_ARCHIVE_PATH = "/tmp/chroma_db.tar.gz"
EMBEDDINGS_COLLECTION_NAME = "feedback_questions"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path=CHROMADB_PATH)
collection = chroma_client.get_or_create_collection(EMBEDDINGS_COLLECTION_NAME)

# Initialize Sentence Transformer model
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

# Function to extract feedback from BigQuery
def extract_feedback_from_bigquery():
    client = bigquery.Client(project=GCP_PROJECT_ID)
    query = f"""
    SELECT user_question, generated_sql, corrected_sql 
    FROM {GCP_PROJECT_ID}.{BQ_DATASET}.{BQ_TABLE}
    WHERE feedback = 'thumbs_down';
    """
    df = client.query(query).to_dataframe()
    df.to_csv(CSV_FILE_PATH, index=False)
    print(f"Extracted {len(df)} rows from BigQuery and saved to {CSV_FILE_PATH}")



# Function to generate embeddings using Sentence Transformer
def generate_embeddings():
    df = pd.read_csv(CSV_FILE_PATH)
    df["question_embedding"] = df["user_question"].apply(lambda text: embedding_model.encode(text).tolist())
    
    # Store embeddings in ChromaDB
    for i, row in df.iterrows():
        collection.add(documents=[row["user_question"]], embeddings=[row["question_embedding"]], ids=[str(i)])
    
    df.to_csv(PROCESSED_CSV_PATH, index=False)
    print("Saved embeddings and processed data.")

# Function to archive and upload ChromaDB
def archive_and_upload_chromadb():
    with tarfile.open(CHROMADB_ARCHIVE_PATH, "w:gz") as tar:
        tar.add(CHROMADB_PATH, arcname=os.path.basename(CHROMADB_PATH))
    print(f"Archived ChromaDB at {CHROMADB_ARCHIVE_PATH}")
