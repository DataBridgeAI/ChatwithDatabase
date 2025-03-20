# from detoxify import Detoxify  # Install using `pip install detoxify`
# import chromadb
# from google.cloud import storage
# import shutil
# import os

# # Configuration
# CHROMA_PATH = "/tmp/chromadb_store"  # Temporary local path to store the ChromaDB data
# GCS_CHROMA_PATH = "bigquery-embeddings-store/RetailDataset/chromadb_store.zip"  # GCS path to your stored ChromaDB zip file
# LOCAL_CHROMA_ZIP_PATH = "/tmp/chromadb_store.zip"  # Local path to store the zip file temporarily

# def download_chromadb_from_gcs():
#     """Download the ChromaDB store from GCS to the local filesystem."""
#     client = storage.Client()
#     bucket = client.bucket('bigquery-embeddings-store')  # Replace with your GCS bucket name
#     blob = bucket.blob(GCS_CHROMA_PATH)  # Path to your ChromaDB store in GCS

#     # Download the ChromaDB zip file
#     blob.download_to_filename(LOCAL_CHROMA_ZIP_PATH)

#     # Extract the zip file to a local directory
#     shutil.unpack_archive(LOCAL_CHROMA_ZIP_PATH, CHROMA_PATH)

# def check_chromadb_validity():
#     """Check if the ChromaDB path is valid and the collection is accessible."""
#     # Step 1: Check if the Chroma store exists locally
#     if not os.path.exists(CHROMA_PATH):
#         print(f"Error: ChromaDB store does not exist at {CHROMA_PATH}")
#         return False

#     # Step 2: Attempt to load the ChromaDB client and collection
#     try:
#         chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
#         collection = chroma_client.get_or_create_collection(name="RetailDataset")  # Replace with your collection name
#         print("ChromaDB store is valid and collection loaded successfully.")
#         return True
#     except Exception as e:
#         print(f"Error loading ChromaDB collection: {str(e)}")
#         return False

# def load_chromadb_client():
#     """Load the ChromaDB client and collection."""
#     # If ChromaDB store is not already downloaded, download it from GCS
#     if not os.path.exists(CHROMA_PATH):
#         download_chromadb_from_gcs()

#     # Check if ChromaDB is valid
#     if check_chromadb_validity():
#         # Initialize ChromaDB client and load the collection
#         chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
#         collection = chroma_client.get_or_create_collection(name="RetailDataset")  # Use the same name as the one used for embeddings
#         return collection
#     else:
#         raise Exception("ChromaDB is not valid. Cannot load the collection.")

# def block_inappropriate_query(user_query):
#     """Block inappropriate queries."""
#     toxic_keywords = ["violence", "illegal", "fake", "prohibited"]
    
#     if any(word in user_query.lower() for word in toxic_keywords):
#         return "Inappropriate query detected."
#     return None


# def check_sql_safety(user_query):
#     """Ensure SQL safety by checking for harmful SQL commands."""
#     sql_blacklist = ["DROP", "DELETE", "ALTER", "INSERT", "TRUNCATE", "UPDATE"]  # Add more keywords if necessary
    
#     # Case-insensitive check for blacklisted SQL commands
#     if any(word in user_query.upper() for word in sql_blacklist):
#         return "Restricted SQL operation detected."
    
#     return None

# def is_toxic(query: str) -> bool:
#     """Check if the query contains toxic language."""
#     toxicity_score = Detoxify('original').predict(query)["toxicity"]
#     return toxicity_score > 0.7  # Threshold (can be adjusted)

# def validate_query(user_query: str) -> str:
#     """Validate query for toxicity and SQL safety."""
#     # First, check if the query contains inappropriate content or toxic language
#     toxic_error = block_inappropriate_query(user_query)
#     if toxic_error:
#         return toxic_error

#     # Then, check for SQL safety issues
#     sql_error = check_sql_safety(user_query)
#     if sql_error:
#         return sql_error

#     # Finally, check if the query is toxic
#     if is_toxic(user_query):
#         return "🚫 Query contains harmful language. Please modify your input."

#     return None  # No issues detected, query is safe


# # Example usage:
# if __name__ == "__main__":
#     # Testing the ChromaDB validity check
#     try:
#         collection = load_chromadb_client()
#         print("ChromaDB loaded successfully.")
#     except Exception as e:
#         print(f"Error: {str(e)}")

from detoxify import Detoxify  # Install using `pip install detoxify`
import chromadb
from google.cloud import storage
import shutil
import os

# Configuration
CHROMA_PATH = "/tmp/chromadb_store"  # Temporary local path to store the ChromaDB data
GCS_CHROMA_PATH = "bigquery-embeddings-store/RetailDataset/chromadb_store.zip"  # GCS path to your stored ChromaDB zip file
LOCAL_CHROMA_ZIP_PATH = "/tmp/chromadb_store.zip"  # Local path to store the zip file temporarily

def download_chromadb_from_gcs():
    """Download the ChromaDB store from GCS to the local filesystem."""
    client = storage.Client()
    bucket = client.bucket('bigquery-embeddings-store')  # Replace with your GCS bucket name
    blob = bucket.blob(GCS_CHROMA_PATH)  # Path to your ChromaDB store in GCS

    # Download the ChromaDB zip file
    blob.download_to_filename(LOCAL_CHROMA_ZIP_PATH)

    # Extract the zip file to a local directory
    shutil.unpack_archive(LOCAL_CHROMA_ZIP_PATH, CHROMA_PATH)

def check_chromadb_validity():
    """Check if the ChromaDB path is valid and the collection is accessible."""
    # Step 1: Check if the Chroma store exists locally
    if not os.path.exists(CHROMA_PATH):
        print(f"Error: ChromaDB store does not exist at {CHROMA_PATH}")
        return False

    # Step 2: Attempt to load the ChromaDB client and collection
    try:
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = chroma_client.get_or_create_collection(name="RetailDataset")  # Replace with your collection name
        print("ChromaDB store is valid and collection loaded successfully.")
        return True
    except Exception as e:
        print(f"Error loading ChromaDB collection: {str(e)}")
        return False

def load_chromadb_client():
    """Load the ChromaDB client and collection."""
    # If ChromaDB store is not already downloaded, download it from GCS
    if not os.path.exists(CHROMA_PATH):
        download_chromadb_from_gcs()

    # Check if ChromaDB is valid
    if check_chromadb_validity():
        # Initialize ChromaDB client and load the collection
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = chroma_client.get_or_create_collection(name="RetailDataset")  # Use the same name as the one used for embeddings
        return collection
    else:
        raise Exception("ChromaDB is not valid. Cannot load the collection.")

def test_chromadb_query(collection):
    """Test if the ChromaDB collection is working by querying it."""
    try:
        # Perform a simple query to check if ChromaDB is accessible
        query = "SELECT * FROM RetailDataset LIMIT 1"  # Example query to test
        result = collection.query(query_embeddings=["test"])  # You can use any dummy query or embeddings
        print(f"ChromaDB Query Result: {result}")
        return True
    except Exception as e:
        print(f"Error while querying ChromaDB: {str(e)}")
        return False

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


# Example usage:
if __name__ == "__main__":
    try:
        # Step 1: Load ChromaDB client and collection
        collection = load_chromadb_client()
        
        # Step 2: Test if ChromaDB is working with a simple query
        if test_chromadb_query(collection):
            print("ChromaDB is valid and accessible.")
        else:
            print("ChromaDB query failed.")
    except Exception as e:
        print(f"Error: {str(e)}")
