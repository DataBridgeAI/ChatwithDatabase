import os
import json
import numpy as np
from google.cloud import storage
from langchain_google_vertexai import VertexAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache

# Configuration Parameters
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
VERTEX_MODEL = "textembedding-gecko@003"
BUCKET_NAME = "bigquery-embeddings-store"
EMBEDDINGS_FILE = "schema_embeddings.json"

# Create embeddings directory if it doesn't exist
EMBEDDINGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'embeddings')
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
LOCAL_EMBEDDINGS_PATH = os.path.join(EMBEDDINGS_DIR, EMBEDDINGS_FILE)

# Initialize Vertex AI Embeddings
embedding_model = VertexAIEmbeddings(model=VERTEX_MODEL)
gcs_client = storage.Client()

@lru_cache(maxsize=1)
def download_and_prepare_embeddings():
    """
    Downloads schema embeddings from GCS and prepares them for search.
    Returns a dictionary of prepared embeddings.
    Cached to prevent multiple downloads.
    """
    try:
        # Step 1: Download from GCS if not exists locally
        if not os.path.exists(LOCAL_EMBEDDINGS_PATH):
            print("📥 Downloading schema embeddings from GCS...")
            bucket = gcs_client.bucket(BUCKET_NAME)
            blob = bucket.blob(EMBEDDINGS_FILE)
            blob.download_to_filename(LOCAL_EMBEDDINGS_PATH)
        
        # Step 2: Load and prepare embeddings
        with open(LOCAL_EMBEDDINGS_PATH, 'r') as f:
            schema_data = json.load(f)
        
        # Step 3: Convert embeddings to numpy arrays for faster comparison
        prepared_embeddings = {}
        for key, value in schema_data.items():
            prepared_embeddings[key] = {
                'embedding': np.array(value['embedding']),
                'semantic_text': value['semantic_text']
            }
        
        return prepared_embeddings
        
    except Exception as e:
        print(f"❌ Error preparing embeddings: {str(e)}")
        return None

def generate_user_input_embedding(user_input):
    """Generate embedding for user input."""
    user_input_embedding = embedding_model.embed_documents([user_input])
    return np.array(user_input_embedding[0])

def check_query_relevance(user_input: str, schema_embeddings=None, threshold: float = 0.75) -> bool:
    """
    Check if the user query is relevant to the schema.
    Args:
        user_input: The user's query string
        schema_embeddings: Pre-loaded schema embeddings (optional)
        threshold: Similarity threshold for relevance
    Returns:
        bool: True if relevant, False if not
    """
    try:
        # Normalize input
        user_input = user_input.lower().strip()
        
        # Generate embedding for user input
        query_embedding = generate_user_input_embedding(user_input)
        
        # Use provided embeddings or load them if not provided
        if schema_embeddings is None:
            schema_embeddings = download_and_prepare_embeddings()
            
        if not schema_embeddings:
            print("❌ Failed to load schema embeddings")
            return False
            
        # Check similarity with schema embeddings
        max_similarity = 0.0
        
        for schema_key, schema_data in schema_embeddings.items():
            schema_embedding = schema_data['embedding'].reshape(1, -1)
            user_embedding = np.array(query_embedding).reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(user_embedding, schema_embedding)[0][0]
            max_similarity = max(max_similarity, similarity)
            
            if max_similarity >= threshold:
                return True
        
        print("❌ Query appears unrelated to the database schema")
        return False
        
    except Exception as e:
        print(f"❌ Error checking query relevance: {str(e)}")
        return False

# Example usage
if __name__ == "__main__":
    print("\n🔍 Query Relevance Checker")
    print("Type 'exit' to quit\n")
    
    while True:
        user_input = input("Enter your query: ")
        if user_input.lower() == 'exit':
            break
            
        is_relevant = check_query_relevance(user_input)
        print(f"Query is {'relevant' if is_relevant else 'not relevant'} to the schema\n")
