import os
from chromadb import PersistentClient
import numpy as np

# Constants
LOCAL_EXTRACT_PATH = "./retrieved_chroma/"

# Define a simple embedding function that returns random vectors
# This is a temporary workaround for the SentenceTransformer compatibility issue
def simple_embedding(text):
    # Generate a deterministic but simple embedding based on the text length
    # This is just a placeholder and won't provide meaningful similarity results
    np.random.seed(hash(text) % 2**32)
    return np.random.rand(384)  # 384 is the dimension of all-MiniLM-L6-v2 embeddings

def retrieve_similar_query(user_query, top_k=1):
    """Finds the most similar past question using ChromaDB."""
    if not os.path.exists(LOCAL_EXTRACT_PATH):
        raise FileNotFoundError("ChromaDB store not found. Ensure it's extracted at startup.")

    # Connect to ChromaDB
    chroma_client = PersistentClient(path=LOCAL_EXTRACT_PATH)
    collection = chroma_client.get_or_create_collection(name="queries")

    # Generate embedding for the user query
    user_embedding = simple_embedding(user_query).tolist()

    # Perform similarity search
    results = collection.query(query_embeddings=[user_embedding], n_results=top_k)

    if results["documents"] and results["metadatas"]:
        similar_query = results["documents"][0][0]
        past_sql = results["metadatas"][0][0]["generated_sql"]
        return similar_query, past_sql

    return None, None  # No similar query found
