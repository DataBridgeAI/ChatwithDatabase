import os
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer, util

# Constants
LOCAL_EXTRACT_PATH = "./retrieved_chroma/"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Initialize embedding model
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

def retrieve_similar_query(user_query, top_k=1, similarity_threshold=0.88):
    """Finds the most similar past question using ChromaDB."""
    if not os.path.exists(LOCAL_EXTRACT_PATH):
        raise FileNotFoundError("ChromaDB store not found. Ensure it's extracted at startup.")

    # Connect to ChromaDB
    chroma_client = PersistentClient(path=LOCAL_EXTRACT_PATH)
    collection = chroma_client.get_or_create_collection(name="queries")

    # Generate embedding for the user query
    user_embedding = embedding_model.encode(user_query)

    # Perform similarity search
    results = collection.query(
        query_embeddings=[user_embedding.tolist()],
        n_results=top_k
    )

    if results["documents"] and results["metadatas"]:
        # Get the first result
        similar_query = results["documents"][0][0]
        past_sql = results["metadatas"][0][0]["generated_sql"]
        
        # Calculate similarity using sentence-transformers
        similar_embedding = embedding_model.encode(similar_query)
        similarity = util.pytorch_cos_sim(
            user_embedding.reshape(1, -1), 
            similar_embedding.reshape(1, -1)
        ).item()

        print(f"Debug - Similarity score: {similarity}")  # Debug print
        print(f"Debug - Similar query: {similar_query}")  # Debug print
        print(f"Debug - User query: {user_query}")  # Debug print
        
        # Lower the threshold slightly for exact matches
        if user_query.lower().strip() == similar_query.lower().strip():
            return similar_query, past_sql
        
        if similarity >= similarity_threshold:
            return similar_query, past_sql

    return None, None  # No sufficiently similar query found