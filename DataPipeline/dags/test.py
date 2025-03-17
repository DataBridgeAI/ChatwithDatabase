# import os
# import zipfile
# import tempfile
# from google.cloud import storage
# from chromadb import PersistentClient
# from sentence_transformers import SentenceTransformer

# # Constants
# BUCKET_NAME = "feedback-questions-embeddings-store"
# ZIP_BLOB_NAME = "chroma_db/persistentdb.zip"  # The stored zip file in GCS
# LOCAL_ZIP_PATH = "retrieved_chroma.zip"
# LOCAL_EXTRACT_PATH = "./retrieved_chroma/"
# EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# # Initialize embedding model
# embedding_model = SentenceTransformer(EMBEDDING_MODEL)

# # Initialize GCS client
# storage_client = storage.Client()

# def download_and_extract_chromadb():
#     """Downloads and extracts the ChromaDB zip from GCS."""
#     bucket = storage_client.bucket(BUCKET_NAME)
#     blob = bucket.blob(ZIP_BLOB_NAME)

#     # Download the zip file
#     blob.download_to_filename(LOCAL_ZIP_PATH)
#     print(f"Downloaded {ZIP_BLOB_NAME} to {LOCAL_ZIP_PATH}")

#     # Extract the zip file
#     with zipfile.ZipFile(LOCAL_ZIP_PATH, "r") as zip_ref:
#         zip_ref.extractall(LOCAL_EXTRACT_PATH)
#     print(f"Extracted ChromaDB store to {LOCAL_EXTRACT_PATH}")

# def retrieve_similar_query(user_query, top_k=1):
#     """Finds the most similar past question using ChromaDB."""
#     # Ensure the ChromaDB store is available
#     if not os.path.exists(LOCAL_EXTRACT_PATH):
#         download_and_extract_chromadb()

#     # Connect to ChromaDB
#     chroma_client = PersistentClient(path=LOCAL_EXTRACT_PATH)
#     collection = chroma_client.get_or_create_collection(name="queries")

#     # Generate embedding for the user query
#     user_embedding = embedding_model.encode(user_query).tolist()

#     # Perform similarity search
#     results = collection.query(query_embeddings=[user_embedding], n_results=top_k)

#     # Retrieve closest match
#     if results["documents"] and results["metadatas"]:
#         similar_query = results["documents"][0][0]
#         past_sql = results["metadatas"][0][0]["generated_sql"]
#         return similar_query, past_sql

#     return None, None  # No similar query found

# # Example Usage
# if __name__ == "__main__":
#     user_query = "How many orders for each customer"
#     similar_query, past_sql = retrieve_similar_query(user_query)

#     if similar_query:
#         print(f"Similar past query: {similar_query}")
#         print(f"Suggested SQL query: {past_sql}")
#     else:
#         print("No similar query found in the database.")
