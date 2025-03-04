from detoxify import Detoxify  # Install using `pip install detoxify`

def block_inappropriate_query(user_query):
    """Block inappropriate queries."""
    toxic_keywords = ["violence", "illegal", "fake", "prohibited"]
    
    if any(word in user_query.lower() for word in toxic_keywords):
        return "Inappropriate query detected."
    return None


def check_sql_safety(user_query):
    """Ensure SQL safety by checking for harmful SQL commands."""
    sql_blacklist = ["DROP", "DELETE", "ALTER", "INSERT", "TRUNCATE", "UPDATE"]  # Add more keywords if necessary
    
    # Case-insensitive check for blacklisted SQL commands
    if any(word in user_query.upper() for word in sql_blacklist):
        return "Restricted SQL operation detected."
    
    return None

def is_toxic(query: str) -> bool:
    """Check if the query contains toxic language."""
    toxicity_score = Detoxify('original').predict(query)["toxicity"]
    return toxicity_score > 0.7  # Threshold (can be adjusted)

def validate_query(user_query: str) -> str:
    """Validate query for toxicity and SQL safety."""
    # First, check if the query contains inappropriate content or toxic language
    toxic_error = block_inappropriate_query(user_query)
    if toxic_error:
        return toxic_error

    # Then, check for SQL safety issues
    sql_error = check_sql_safety(user_query)
    if sql_error:
        return sql_error

    # Finally, check if the query is toxic
    if is_toxic(user_query):
        return "🚫 Query contains harmful language. Please modify your input."

    return None  # No issues detected, query is safe


# import chromadb
# import shutil
# import os
# import json
# import google.generativeai as genai  # For toxicity check
# from langchain_google_vertexai import VertexAIEmbeddings
# from google.cloud import storage

# # Configuration
# PROJECT_ID = "chatwithdata-451800"
# DATASET_ID = "RetailDataset"
# BUCKET_NAME = "bigquery-embeddings-store"
# CHROMA_PATH = "/tmp/chromadb_store"
# GCS_CHROMA_PATH = f"{DATASET_ID}/chromadb_store.zip"
# VERTEX_MODEL = "textembedding-gecko@003"

# # Initialize Vertex AI Embeddings
# embedding_model = VertexAIEmbeddings(model=VERTEX_MODEL)

# # Initialize Gemini model for toxicity detection
# genai.configure(api_key="YOUR_GEMINI_API_KEY")
# safety_model = genai.GenerativeModel("gemini-pro")  

# def load_embeddings_from_gcs():
#     """Download the latest ChromaDB embeddings store from GCS and extract it."""
#     client = storage.Client()
#     bucket = client.bucket(BUCKET_NAME)
#     blob = bucket.blob(GCS_CHROMA_PATH)

#     zip_path = "/tmp/chromadb_store.zip"
#     blob.download_to_filename(zip_path)
#     shutil.unpack_archive(zip_path, CHROMA_PATH)

# def check_toxicity(user_query: str) -> bool:
#     """Check if the user query contains harmful language."""
#     safety_response = safety_model.generate_content(f"Analyze this query for toxicity: {user_query}. Is it toxic? Answer only with 'yes' or 'no'.")
    
#     # Extract the response text
#     response_text = safety_response.text.strip().lower()
#     return response_text == "yes"

# def validate_query(user_query: str) -> str:
#     """Check for toxicity and schema relevance of the query."""
    
#     # Step 1: Check for toxicity
#     if check_toxicity(user_query):
#         return "🚫 Query contains harmful language. Please modify your input."

#     # Step 2: Load embeddings if not present
#     if not os.path.exists(CHROMA_PATH):
#         load_embeddings_from_gcs()

#     # Step 3: Connect to ChromaDB
#     chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
#     collection = chroma_client.get_or_create_collection(name=DATASET_ID)

#     # Step 4: Get user query embedding
#     query_embedding = embedding_model.embed_query(user_query)

#     # Step 5: Perform semantic search
#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=1  # Fetch top match
#     )

#     # Step 6: Check if the query is relevant to schema
#     if not results["ids"] or len(results["ids"][0]) == 0:
#         return "❌ Query is not relevant to the available database schema. Please refine your question."

#     return "✅ Query is safe and relevant."


