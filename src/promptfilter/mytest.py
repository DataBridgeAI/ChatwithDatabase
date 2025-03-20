import json
import numpy as np
from google.cloud import storage
from langchain_google_vertexai import VertexAIEmbeddings
import os
from sklearn.metrics.pairwise import cosine_similarity
import chromadb
import shutil
from chroma_setup import extract_embeddings

# Configuration
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
BUCKET_NAME = "bigquery-embeddings-store"
VERTEX_MODEL = "textembedding-gecko@003"

# Initialize Vertex AI Embeddings
embedding_model = VertexAIEmbeddings(model=VERTEX_MODEL)

def download_schema_embeddings():
    """Download schema embeddings from GCS bucket"""
    try:
        # Setup paths
        local_zip_path = "/tmp/chromadb_store.zip"
        local_chroma_path = "/tmp/chromadb_store"
        
        # Clean up existing files if they exist
        if os.path.exists(local_zip_path):
            os.remove(local_zip_path)
        if os.path.exists(local_chroma_path):
            shutil.rmtree(local_chroma_path)
        
        # Create fresh directory
        os.makedirs(local_chroma_path, exist_ok=True)
        
        # Download ChromaDB zip from GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{DATASET_ID}/chromadb_store.zip")
        blob.download_to_filename(local_zip_path)
        
        # Extract the zip file
        shutil.unpack_archive(local_zip_path, local_chroma_path, 'zip')
        
        # Initialize ChromaDB client
        chroma_client = chromadb.PersistentClient(path=local_chroma_path)
        collection = chroma_client.get_or_create_collection(name=DATASET_ID)
        
        # Get all embeddings with their metadata and documents
        results = collection.get(
            include=['documents', 'embeddings', 'metadatas']
        )
        
        if not results or len(results['documents']) == 0:
            raise Exception("No embeddings found in ChromaDB collection")
            
        # Convert to schema_embeddings format
        schema_embeddings = {}
        for idx, (doc, embedding, metadata) in enumerate(zip(results['documents'], 
                                                           results['embeddings'], 
                                                           results['metadatas'])):
            # Reconstruct the ID from metadata
            embedding_id = f"{metadata['table']}:{metadata['column']}"
            schema_embeddings[embedding_id] = {
                'embedding': embedding,
                'semantic_text': doc
            }
        
        print(f"✅ Successfully downloaded schema embeddings for {len(schema_embeddings)} columns")
        return schema_embeddings
        
    except Exception as e:
        print(f"❌ Error downloading schema embeddings: {str(e)}")
        return None

def generate_user_input_embedding(user_input):
    """Generate embedding for user input"""
    try:
        user_input_embedding = embedding_model.embed_documents([user_input])
        return np.array(user_input_embedding[0])
    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return None

def find_top_matches(user_input, schema_embeddings, top_n=5, threshold=0.75):
    """Find top matching schema based on semantic similarity"""
    user_input_embedding = generate_user_input_embedding(user_input)
    if user_input_embedding is None:
        return []
        
    similarities = {}
    
    for schema_key, schema_data in schema_embeddings.items():
        schema_embedding = np.array(schema_data['embedding']).reshape(1, -1)
        user_embedding = np.array(user_input_embedding).reshape(1, -1)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(user_embedding, schema_embedding)[0][0]
        similarities[schema_key] = {
            'score': similarity,
            'semantic_text': schema_data['semantic_text']
        }
    
    # Sort by similarity score and filter based on threshold
    sorted_matches = sorted(
        [(k, v) for k, v in similarities.items() if v['score'] >= threshold],
        key=lambda x: x[1]['score'],
        reverse=True
    )
    
    if not sorted_matches:
        print("Sorry, no relevant schema found.")
        return []
    
    print(f"\nTop {top_n} matching table-column pairs for user input '{user_input}':")
    for idx, (schema_key, data) in enumerate(sorted_matches[:top_n], 1):
        print(f"{idx}. {schema_key}")
        print(f"   Score: {data['score']:.2f}")
        print(f"   Context: {data['semantic_text']}\n")
    
    return sorted_matches[:top_n]

def process_user_input(user_input, schema_embeddings):
    """Process user input and find relevant schema matches"""
    try:
        return find_top_matches(user_input, schema_embeddings)
    except Exception as e:
        print(f"Error processing user input: {str(e)}")
        return []

def main():
    """Main function to run the semantic search demo"""
    print("🔍 Semantic Search Demo")
    print("Type 'exit' to quit\n")
    
    # Download schema embeddings once at startup
    schema_embeddings = extract_embeddings()
    if schema_embeddings is None:
        print("❌ Failed to load schema embeddings. Exiting.")
        return
    
    while True:
        user_input = input("\nEnter a query (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        
        process_user_input(user_input, schema_embeddings)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")
