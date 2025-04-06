import os
import shutil
from chromadb import PersistentClient
import numpy as np

# Constants
LOCAL_EXTRACT_PATH = "./retrieved_chroma/"

def simple_embedding(text):
    # Generate a deterministic but simple embedding based on the text
    np.random.seed(hash(text) % 2**32)
    return np.random.rand(384).tolist()  # 384 is the dimension of all-MiniLM-L6-v2 embeddings

def download_and_extract_chromadb():
    """Creates a mock ChromaDB for local development."""
    if os.path.exists(LOCAL_EXTRACT_PATH):
        print("ChromaDB already exists, skipping creation.")
        return

    # Create the directory
    os.makedirs(LOCAL_EXTRACT_PATH, exist_ok=True)
    print(f"Created directory {LOCAL_EXTRACT_PATH}")

    # Create a mock ChromaDB
    try:
        client = PersistentClient(path=LOCAL_EXTRACT_PATH)
        collection = client.create_collection(name="queries")

        # Add some sample data
        sample_queries = [
            "Show me the top 10 products by sales",
            "What are the most popular categories?",
            "List customers who spent more than $1000"
        ]

        sample_sql = [
            "SELECT product_name, SUM(sales) FROM products GROUP BY product_name ORDER BY SUM(sales) DESC LIMIT 10",
            "SELECT category_name, COUNT(*) FROM categories JOIN products ON categories.id = products.category_id GROUP BY category_name ORDER BY COUNT(*) DESC",
            "SELECT customer_name FROM customers WHERE total_spent > 1000"
        ]

        # Add documents to the collection
        collection.add(
            documents=sample_queries,
            embeddings=[simple_embedding(q) for q in sample_queries],
            metadatas=[{"generated_sql": sql} for sql in sample_sql],
            ids=[f"id{i}" for i in range(len(sample_queries))]
        )

        print("Created mock ChromaDB with sample data")
    except Exception as e:
        print(f"Error creating mock ChromaDB: {str(e)}")
        # If there was an error, clean up
        if os.path.exists(LOCAL_EXTRACT_PATH):
            shutil.rmtree(LOCAL_EXTRACT_PATH)
            os.makedirs(LOCAL_EXTRACT_PATH, exist_ok=True)
