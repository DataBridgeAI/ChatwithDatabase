import os
import numpy as np
from functools import lru_cache

# Define a simple cosine similarity function
def cosine_similarity(a, b):
    # Compute the dot product
    dot_product = np.dot(a, b.T)
    # Compute the L2 norms
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    # Compute the cosine similarity
    return dot_product / (norm_a * norm_b)

# Configuration Parameters
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
EMBEDDINGS_FILE = "schema_embeddings.json"

# Create embeddings directory if it doesn't exist
EMBEDDINGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'embeddings')
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
LOCAL_EMBEDDINGS_PATH = os.path.join(EMBEDDINGS_DIR, EMBEDDINGS_FILE)

# Define a simple embedding function
def simple_embedding(text):
    # Generate a deterministic but simple embedding based on the text
    np.random.seed(hash(text) % 2**32)
    return np.random.rand(768)  # 768 is a common embedding dimension

@lru_cache(maxsize=1)
def download_and_prepare_embeddings():
    """
    Creates mock schema embeddings for testing.
    Returns a dictionary of prepared embeddings.
    Cached to prevent multiple calculations.
    """
    try:
        # Create mock schema embeddings
        tables = ["customers", "orders", "products", "categories"]
        prepared_embeddings = {}

        for table in tables:
            prepared_embeddings[table] = {
                'embedding': simple_embedding(table),
                'semantic_text': f"Information about {table}"
            }

        return prepared_embeddings

    except Exception as e:
        print(f"❌ Error preparing embeddings: {str(e)}")
        return None

def generate_user_input_embedding(user_input):
    """Generate embedding for user input."""
    return simple_embedding(user_input)

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

        for _, schema_data in schema_embeddings.items():
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
