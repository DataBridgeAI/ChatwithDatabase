import os
import json
import numpy as np
from google.cloud import bigquery, storage
from langchain_google_vertexai import VertexAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

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

def download_and_prepare_embeddings():
    """
    Downloads schema embeddings from GCS and prepares them for search.
    Returns a dictionary of prepared embeddings.
    """
    try:
        # Step 1: Download from GCS if not exists locally
        if not os.path.exists(LOCAL_EMBEDDINGS_PATH):
            print("📥 Downloading schema embeddings from GCS...")
            bucket = gcs_client.bucket(BUCKET_NAME)
            blob = bucket.blob(EMBEDDINGS_FILE)
            blob.download_to_filename(LOCAL_EMBEDDINGS_PATH)
            print("✅ Download complete")
        
        # Step 2: Load and prepare embeddings
        print("🔄 Loading schema embeddings...")
        with open(LOCAL_EMBEDDINGS_PATH, 'r') as f:
            schema_data = json.load(f)
        
        # Step 3: Convert embeddings to numpy arrays for faster comparison
        prepared_embeddings = {}
        for key, value in schema_data.items():
            prepared_embeddings[key] = {
                'embedding': np.array(value['embedding']),
                'semantic_text': value['semantic_text']
            }
        
        print(f"✅ Successfully prepared {len(prepared_embeddings)} embeddings for search")
        return prepared_embeddings
        
    except Exception as e:
        print(f"❌ Error preparing embeddings: {str(e)}")
        return None

def generate_user_input_embedding(user_input):
    """Generate embedding for user input."""
    user_input_embedding = embedding_model.embed_documents([user_input])
    return np.array(user_input_embedding[0])

def check_query_relevance(user_input: str, threshold: float = 0.75) -> bool:
    """
    Check if the user query is relevant to the schema.
    Returns True if relevant, False if not.
    """
    try:
        # Generate embedding for user input
        query_embedding = generate_user_input_embedding(user_input)
        
        # Load prepared embeddings
        schema_embeddings = download_and_prepare_embeddings()
        if not schema_embeddings:
            print("❌ Failed to load schema embeddings")
            return False
            
        # Check similarity with schema embeddings
        similarities = {}
    
        for schema_key, schema_data in schema_embeddings.items():
            schema_embedding = np.array(schema_data['embedding']).reshape(1, -1)
            user_embedding = np.array(query_embedding).reshape(1, -1)
        
            # Calculate cosine similarity
            similarity = cosine_similarity(user_embedding, schema_embedding)[0][0]
            similarities[schema_key] = {
                'score': similarity,
                'semantic_text': schema_data['semantic_text']
            }
    
        # Check if any similarity scores meet the threshold
        relevant_matches = [v['score'] for v in similarities.values() if v['score'] >= threshold]
        
        if not relevant_matches:
            print("❌ Query appears unrelated to the database schema")
            return False
            
        return True
        
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
