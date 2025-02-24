from schema_drift_checker import detect_schema_drift
from embedding_generator import generate_schema_embeddings

def update_embeddings_if_drift():
    """Triggers schema embedding update if drift is detected."""
    if detect_schema_drift():
        print("Updating schema embeddings due to detected drift...")
        generate_schema_embeddings()
        print("Schema embeddings updated.")
    else:
        print("No update needed.")

if __name__ == "__main__":
    update_embeddings_if_drift()
