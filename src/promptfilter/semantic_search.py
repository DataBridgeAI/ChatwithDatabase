import os
import json
import numpy as np
import zipfile
import shutil
import traceback
from google.cloud import storage
from langchain_google_vertexai import VertexAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import Dict, List, Tuple, Any, Optional
import chromadb
from chromadb.config import Settings
import gc
import time
from rapidfuzz import fuzz, process

# Configuration Parameters
DEFAULT_PROJECT_ID = "chatwithdata-451800"
VERTEX_MODEL = "textembedding-gecko@003"
BUCKET_NAME = "bigquery-embeddings-store"

# Initialize Vertex AI Embeddings
print("Initializing VertexAI embedding model...")
embedding_model = VertexAIEmbeddings(model=VERTEX_MODEL)
gcs_client = storage.Client()
print("Initialized storage client and embedding model")

# Cache to store vector DBs and embeddings by dataset_id
VECTOR_DB_CACHE = {}
EMBEDDINGS_CACHE = {}

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def setup_chroma_client(dataset_id: str) -> chromadb.PersistentClient:
    embeddings_dir = os.path.join(os.path.dirname(__file__), '..', 'embeddings')
    os.makedirs(embeddings_dir, exist_ok=True)
    chroma_persist_dir = os.path.join(embeddings_dir, f'chroma_{dataset_id}')
    os.makedirs(chroma_persist_dir, exist_ok=True)
    return chromadb.PersistentClient(path=chroma_persist_dir)

def download_and_extract_chroma_db(dataset_id: str) -> Optional[str]:
    embeddings_dir = os.path.join(os.path.dirname(__file__), '..', 'embeddings')
    os.makedirs(embeddings_dir, exist_ok=True)
    local_db_path = os.path.join(embeddings_dir, f'chroma_{dataset_id}')
    local_zip_path = os.path.join(embeddings_dir, f'schema_chroma_{dataset_id}.zip')

    if os.path.exists(local_db_path) and os.listdir(local_db_path):
        print(f"🔄 Using cached ChromaDB for dataset {dataset_id}")
        return local_db_path

    if os.path.exists(local_zip_path):
        try:
            os.remove(local_zip_path)
        except Exception as e:
            print(f"⚠️ Warning: Could not remove zip file: {str(e)}")

    if os.path.exists(local_db_path):
        try:
            gc.collect()
            shutil.rmtree(local_db_path, ignore_errors=True)
        except Exception as e:
            print(f"⚠️ Warning: Could not remove DB directory: {str(e)}")
            timestamp = int(time.time())
            local_db_path = os.path.join(embeddings_dir, f'chroma_{dataset_id}_{timestamp}')

    os.makedirs(local_db_path, exist_ok=True)

    try:
        print(f"📅 Downloading ChromaDB for dataset {dataset_id}...")
        bucket = gcs_client.bucket(BUCKET_NAME)
        gcs_zip_path = f"{dataset_id}/schema_chroma.zip"
        blob = bucket.blob(gcs_zip_path)

        if not blob.exists():
            gcs_zip_path = f"chroma_db/{dataset_id}/schema_chroma.zip"
            blob = bucket.blob(gcs_zip_path)
            if not blob.exists():
                gcs_zip_path = f"chroma_db/schema_chroma.zip"
                blob = bucket.blob(gcs_zip_path)
                if not blob.exists():
                    print(f"❌ Could not find ChromaDB zip for {dataset_id}")
                    return None

        print(f"Downloading from: {gcs_zip_path}")
        blob.download_to_filename(local_zip_path)
        print(f"✅ Download complete: {local_zip_path}")

        print(f"Extracting to: {local_db_path}")
        with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
            zip_ref.extractall(local_db_path)

        print(f"✅ Extraction complete: {local_db_path}")
        print(f"Extracted files: {os.listdir(local_db_path)}")

        try:
            os.remove(local_zip_path)
        except:
            pass

        return local_db_path

    except Exception as e:
        print(f"❌ Error downloading/extracting ChromaDB: {str(e)}")
        traceback.print_exc()
        return None

def get_vector_db(dataset_id: str) -> Optional[chromadb.Collection]:
    global VECTOR_DB_CACHE

    embeddings_dir = os.path.join(os.path.dirname(__file__), '..', 'embeddings')
    local_db_path = os.path.join(embeddings_dir, f'chroma_{dataset_id}')

    if os.path.exists(local_db_path) and os.listdir(local_db_path):
        print(f"📂 Found local ChromaDB at {local_db_path}")
        db_path = local_db_path
    else:
        print(f"📦 Local ChromaDB not found for {dataset_id}, attempting to download...")
        db_path = download_and_extract_chroma_db(dataset_id)
        if not db_path:
            print(f"❌ Could not load vector DB for dataset {dataset_id}")
            return None

    try:
        client = chromadb.PersistentClient(path=db_path)

        collection_patterns = [
            f"schema_embeddings_{dataset_id}",
            "schema_embeddings",
            dataset_id,
            "embeddings"
        ]

        try:
            collection_names = client.list_collections()
            print(f"Available collections: {collection_names}")
        except Exception as e:
            print(f"⚠️ Error listing collections: {str(e)}")
            collection_names = []

        collection = None
        for pattern in collection_patterns:
            if pattern in collection_names:
                try:
                    collection = client.get_collection(pattern)
                    print(f"✅ Found collection: {pattern}")
                    break
                except Exception as e:
                    print(f"⚠️ Error getting collection {pattern}: {str(e)}")

        if collection is None and collection_names:
            try:
                collection = client.get_collection(collection_names[0])
                print(f"Fallback to first available collection: {collection_names[0]}")
            except Exception as e:
                print(f"❌ Failed to load fallback collection: {str(e)}")
                return None

        VECTOR_DB_CACHE[dataset_id] = collection
        return collection

    except Exception as e:
        print(f"❌ Error setting up ChromaDB for dataset {dataset_id}: {str(e)}")
        traceback.print_exc()
        return None

def download_and_extract_chroma_db(dataset_id: str) -> Optional[str]:
    """
    Download and extract the ChromaDB zip file for a dataset.
    Returns the path to the extracted ChromaDB directory.
    """
    # Create embeddings directory inside src/embeddings/
    embeddings_dir = os.path.join(os.path.dirname(__file__), '..', 'embeddings')
    os.makedirs(embeddings_dir, exist_ok=True)

    # Define dataset-specific path
    local_db_path = os.path.join(embeddings_dir, f'chroma_{dataset_id}')
    local_zip_path = os.path.join(embeddings_dir, f'schema_chroma_{dataset_id}.zip')

    # Check if already extracted
    if os.path.exists(local_db_path) and os.listdir(local_db_path):
        print(f"🔄 Using cached ChromaDB for dataset {dataset_id}")
        return local_db_path

    # Clean up previous partials
    if os.path.exists(local_zip_path):
        try:
            os.remove(local_zip_path)
        except Exception as e:
            print(f"⚠️ Warning: Could not remove zip file: {str(e)}")

    if os.path.exists(local_db_path):
        try:
            gc.collect()  # Clean up any open connections
            shutil.rmtree(local_db_path, ignore_errors=True)
        except Exception as e:
            print(f"⚠️ Warning: Could not remove DB directory: {str(e)}")
            timestamp = int(time.time())
            local_db_path = os.path.join(embeddings_dir, f'chroma_{dataset_id}_{timestamp}')

    # Prepare for new extraction
    os.makedirs(local_db_path, exist_ok=True)

    try:
        print(f"📥 Downloading ChromaDB for dataset {dataset_id}...")

        bucket = gcs_client.bucket(BUCKET_NAME)
        gcs_zip_path = f"{dataset_id}/schema_chroma.zip"
        blob = bucket.blob(gcs_zip_path)

        if not blob.exists():
            gcs_zip_path = f"chroma_db/{dataset_id}/schema_chroma.zip"
            blob = bucket.blob(gcs_zip_path)

            if not blob.exists():
                gcs_zip_path = f"chroma_db/schema_chroma.zip"
                blob = bucket.blob(gcs_zip_path)

                if not blob.exists():
                    print(f"❌ Could not find ChromaDB zip for {dataset_id}")
                    return None

        print(f"Downloading from: {gcs_zip_path}")
        blob.download_to_filename(local_zip_path)
        print(f"✅ Download complete: {local_zip_path}")

        print(f"Extracting to: {local_db_path}")
        with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
            zip_ref.extractall(local_db_path)

        print(f"✅ Extraction complete: {local_db_path}")
        print(f"Extracted files: {os.listdir(local_db_path)}")

        try:
            os.remove(local_zip_path)
        except:
            pass

        return local_db_path

    except Exception as e:
        print(f"❌ Error downloading/extracting ChromaDB: {str(e)}")
        traceback.print_exc()
        return None

def download_and_prepare_embeddings(dataset_id: str):
    """
    Gets schema keys and embeddings from ChromaDB.
    This function now serves as an adapter to maintain compatibility with the rest of the code.
    """
    global EMBEDDINGS_CACHE
    
    # Return from cache if available
    if dataset_id in EMBEDDINGS_CACHE:
        return EMBEDDINGS_CACHE[dataset_id]
    
    try:
        # Get the ChromaDB collection
        collection = get_vector_db(dataset_id)
        if not collection:
            print(f"❌ Could not get ChromaDB collection for {dataset_id}")
            return None
        
        # Get all documents and embeddings from the collection
        result = collection.get(include=["embeddings", "documents", "metadatas"])
        
        # Convert to the expected format
        prepared_embeddings = {}
        for i, doc_id in enumerate(result["ids"]):
            # Check if we have embeddings for this document
            if i < len(result["embeddings"]):
                prepared_embeddings[doc_id] = {
                    'embedding': np.array(result["embeddings"][i]),
                    'semantic_text': result["documents"][i] if i < len(result["documents"]) else ""
                }
        
        # Cache the embeddings
        EMBEDDINGS_CACHE[dataset_id] = prepared_embeddings
        
        return prepared_embeddings
        
    except Exception as e:
        print(f"❌ Error preparing embeddings for {dataset_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def list_available_datasets() -> List[str]:
    """
    List available datasets from GCS bucket
    """
    try:
        print(f"Listing available datasets from bucket: {BUCKET_NAME}")
        bucket = gcs_client.bucket(BUCKET_NAME)
        
        # Based on your folder structure, look for schema_chroma.zip files
        datasets = set()
        
        # Look for pattern: DATASET_ID/schema_chroma.zip
        for blob in bucket.list_blobs():
            if blob.name.endswith('schema_chroma.zip'):
                # Extract the dataset ID from the path
                parts = blob.name.split('/')
                if len(parts) >= 2:
                    # The dataset ID is the directory name
                    dataset_id = parts[0]
                    if dataset_id and dataset_id != "chroma_db":
                        datasets.add(dataset_id)
        
        # Also check for chroma_db/DATASET_ID/schema_chroma.zip pattern
        prefix = "chroma_db/"
        for blob in bucket.list_blobs(prefix=prefix):
            parts = blob.name.split('/')
            if len(parts) >= 3 and parts[len(parts)-1] == "schema_chroma.zip":
                dataset_id = parts[1]
                if dataset_id:
                    datasets.add(dataset_id)
        
        result = sorted(list(datasets))
        print(f"Found datasets: {', '.join(result)}")
        return result
    except Exception as e:
        print(f"❌ Error listing datasets: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def generate_user_input_embedding(user_input: str) -> np.ndarray:
    """Generate embedding for user input."""
    user_input_embedding = embedding_model.embed_documents([user_input])
    return np.array(user_input_embedding[0])

def extract_potential_schema_terms(query: str) -> List[str]:
    """
    Extract potential schema-related terms from the query.
    This is schema-agnostic and doesn't assume any specific column names.
    """
    # Split the query into individual words and clean them
    words = preprocess_text(query).split()
    
    # Filter out common SQL keywords and stopwords that are unlikely to be schema elements
    sql_keywords = {
        'select', 'from', 'where', 'join', 'and', 'or', 'not', 'like', 'in', 'between',
        'group', 'by', 'having', 'order', 'limit', 'offset', 'union', 'all', 'distinct',
        'as', 'on', 'using', 'inner', 'outer', 'left', 'right', 'full', 'case', 'when',
        'then', 'else', 'end', 'is', 'null', 'true', 'false', 'asc', 'desc', 'with'
    }
    
    common_stopwords = {
        'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'by', 
        'over', 'about', 'above', 'across', 'after', 'against', 'along', 'among', 
        'around', 'because', 'before', 'behind', 'below', 'beneath', 'beside', 
        'between', 'beyond', 'during', 'except', 'inside', 'into', 'near', 'of', 
        'off', 'since', 'through', 'throughout', 'under', 'until', 'up', 'upon', 
        'with', 'within', 'without', 'i', 'we', 'you', 'he', 'she', 'it', 'they',
        'me', 'us', 'him', 'her', 'them'
    }
    
    # Extract potential schema terms (words not in the exclusion sets)
    potential_terms = [word for word in words if word not in sql_keywords and word not in common_stopwords]
    
    # Extract multi-word phrases (for potential table or column names with underscores)
    # Pattern-based approach without hardcoding specific names
    text = preprocess_text(query)
    
    # Look for phrases around SQL-related terms (potential table/field references)
    phrase_patterns = [
        r'from\s+([a-z0-9_]+)',  # Tables after FROM
        r'join\s+([a-z0-9_]+)',  # Tables after JOIN
        r'select\s+([a-z0-9_\s,]+)\s+from',  # Columns in SELECT
        r'where\s+([a-z0-9_]+)',  # Fields in WHERE
        r'group\s+by\s+([a-z0-9_\s,]+)',  # Fields in GROUP BY
        r'order\s+by\s+([a-z0-9_\s,]+)'   # Fields in ORDER BY
    ]
    
    for pattern in phrase_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            # Split by commas for multiple fields and strip whitespace
            parts = [part.strip() for part in match.split(',')]
            potential_terms.extend(parts)
    
    # Remove duplicates and empty strings
    potential_terms = list(set([term for term in potential_terms if term]))
    
    return potential_terms

def find_fuzzy_matches(schema_keys: List[str], query_terms: List[str]) -> List[Dict[str, Any]]:
    """
    Find fuzzy matches between query terms and schema elements.
    This is schema-agnostic and doesn't assume anything about the structure.
    
    Args:
        schema_keys: List of schema element keys (table:column format)
        query_terms: Potential schema-related terms extracted from the query
        
    Returns:
        List of matches with scores
    """
    if not query_terms or not schema_keys:
        return []
    
    # Extract all tables and columns from schema keys
    tables = set()
    columns = set()
    
    for key in schema_keys:
        parts = key.split(':')
        if len(parts) >= 2:
            tables.add(parts[0])
            columns.add(parts[1])
    
    # Convert to lists for processing
    tables_list = list(tables)
    columns_list = list(columns)
    
    # Find fuzzy matches for each query term
    fuzzy_matches = []
    
    for term in query_terms:
        if len(term) < 3:  # Skip very short terms
            continue
        
        # Check against tables
        table_matches = process.extract(
            term, 
            tables_list, 
            scorer=fuzz.ratio, 
            limit=3, 
            score_cutoff=70
        )
        
        for table, score, _ in table_matches:
            # Find all schema keys for this table
            related_keys = [k for k in schema_keys if k.startswith(f"{table}:")]
            
            for key in related_keys:
                fuzzy_matches.append({
                    "schema_element": key,
                    "matched_term": term,
                    "matched_on": "table",
                    "match_score": score * 0.01  # Convert percentage to 0-1 scale
                })
        
        # Check against columns
        column_matches = process.extract(
            term, 
            columns_list, 
            scorer=fuzz.ratio, 
            limit=3, 
            score_cutoff=70
        )
        
        for column, score, _ in column_matches:
            # Find all schema keys for this column
            related_keys = [k for k in schema_keys if k.endswith(f":{column}")]
            
            for key in related_keys:
                fuzzy_matches.append({
                    "schema_element": key,
                    "matched_term": term,
                    "matched_on": "column",
                    "match_score": score * 0.01  # Convert percentage to 0-1 scale
                })
    
    # Remove duplicates and sort by score
    unique_matches = {}
    for match in fuzzy_matches:
        key = match["schema_element"]
        if key not in unique_matches or match["match_score"] > unique_matches[key]["match_score"]:
            unique_matches[key] = match
    
    return sorted(list(unique_matches.values()), key=lambda x: x["match_score"], reverse=True)

def check_query_relevance(user_input: str, dataset_id: str, project_id: str = None, threshold: float = 0.70) -> bool:
    try:
        project_id = project_id or DEFAULT_PROJECT_ID
        print(f"\nDEBUG: Checking relevance for query: '{user_input}'")
        
        # Step 1: Preprocess input
        processed_input = preprocess_text(user_input)
        
        # Step 2: Get vector DB directly
        vector_db = get_vector_db(dataset_id)
        if not vector_db:
            print(f"DEBUG: Vector DB not found for dataset {dataset_id}")
            return False

        # Log the actual similarity score for debugging
        print(f"DEBUG: Processed input: '{processed_input}'")
        print(f"DEBUG: Using threshold: {threshold}")
        
        # Step 3: Get schema information from the vector DB
        try:
            # Get all schema keys from the collection
            schema_result = vector_db.get(include=["metadatas"])
            schema_keys = schema_result["ids"]
            print(f"Found {len(schema_keys)} schema keys")
        except Exception as e:
            print(f"❌ Error getting schema keys: {str(e)}")
            return False
        
        # Step 4: Extract potential schema terms
        schema_terms = extract_potential_schema_terms(user_input)
        print(f"Extracted schema terms: {schema_terms}")
        
        # Step 5: Find fuzzy matches
        fuzzy_matches = find_fuzzy_matches(schema_keys, schema_terms)
        
        # Step 6: Generate embedding for user input
        query_embedding = generate_user_input_embedding(processed_input)
        
        # Step 7: Query the vector DB
        try:
            results = vector_db.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=5,
                include=["documents", "distances", "metadatas"]
            )
            
            # Process semantic matches
            semantic_matches = []
            for i, (doc_id, distance) in enumerate(zip(results['ids'][0], results['distances'][0])):
                similarity = 1.0 - distance
                semantic_text = results['documents'][0][i] if i < len(results['documents'][0]) else ""
                semantic_matches.append({
                    "schema_element": doc_id,
                    "similarity": similarity,
                    "semantic_text": semantic_text,
                    "matched_on": "semantic"
                })
        except Exception as e:
            print(f"❌ Error querying vector DB: {str(e)}")
            # If we have fuzzy matches, we can still proceed
            if not fuzzy_matches:
                return False
            semantic_matches = []
        
        # Step 8: Combine matches
        all_matches = []
        
        # Add semantic matches
        all_matches.extend([{
            "schema_element": match["schema_element"],
            "score": match["similarity"],
            "match_type": "semantic",
            "matched_on": "semantic",
            "semantic_text": match["semantic_text"]
        } for match in semantic_matches])
        
        # Add fuzzy matches
        for match in fuzzy_matches:
            # Find semantic text from semantic matches if available
            semantic_text = next((
                sm["semantic_text"] for sm in semantic_matches 
                if sm["schema_element"] == match["schema_element"]
            ), "")
            
            all_matches.append({
                "schema_element": match["schema_element"],
                "score": match["match_score"] * 0.9,  # Slightly downweight fuzzy matches
                "match_type": "fuzzy",
                "matched_on": match["matched_on"],
                "matched_term": match["matched_term"],
                "semantic_text": semantic_text
            })
        
        # Step 9: Merge and sort matches
        unique_matches = {}
        for match in all_matches:
            key = match["schema_element"]
            if key not in unique_matches or match["score"] > unique_matches[key]["score"]:
                unique_matches[key] = match
        
        top_matches = sorted(list(unique_matches.values()), key=lambda x: x["score"], reverse=True)
        
        # Print top matches
        if top_matches:
            print("Top matches:")
            for i, match in enumerate(top_matches[:3]):
                print(f"  {i+1}. {match['schema_element']} ({match['match_type']}, score: {match['score']:.2f})")
                
        # Step 10: Calculate final score
        combined_score = 0.0
        if top_matches:
            combined_score = top_matches[0]["score"]
            
            matched_terms = set()
            matched_tables = set()
            matched_columns = set()
            
            for match in top_matches[:5]:
                if "matched_term" in match:
                    matched_terms.add(match["matched_term"])
                
                schema_key = match["schema_element"]
                parts = schema_key.split(":")
                if len(parts) >= 2:
                    matched_tables.add(parts[0])
                    matched_columns.add(parts[1])
            
            if schema_terms and matched_terms:
                term_match_ratio = len(matched_terms) / len(schema_terms)
                term_boost = min(term_match_ratio * 0.1, 0.1)
                combined_score = min(combined_score + term_boost, 1.0)
            
            schema_diversity_boost = min((len(matched_tables) + len(matched_columns)) * 0.01, 0.1)
            combined_score = min(combined_score + schema_diversity_boost, 1.0)
        
        # Step 11: Determine relevance
        is_relevant = combined_score >= threshold
        print(f"Final relevance score: {combined_score:.2f} (threshold: {threshold})")
        print(f"Query is {'RELEVANT' if is_relevant else 'NOT RELEVANT'} to the schema")
        
        return is_relevant
        
    except Exception as e:
        print(f"❌ Error checking query relevance: {str(e)}")
        import traceback
        traceback.print_exc()
        return False  # Changed to return False (NOT RELEVANT) in case of errors

def main():
    """
    Main function to run the semantic search tool
    """
    print("\n🔍 Schema-Agnostic Query Relevance Checker")
    print("Type 'exit' to quit\n")
    
    # List available datasets
    available_datasets = list_available_datasets()
    print(f"Available datasets: {', '.join(available_datasets) if available_datasets else 'None'}")
    
    # Prompt for dataset ID if none selected
    current_dataset_id = None
    while not current_dataset_id:
        dataset_input = input("\nEnter dataset ID to use: ")
        
        if dataset_input.lower() == 'exit':
            print("Exiting program.")
            return
            
        if dataset_input in available_datasets:
            current_dataset_id = dataset_input
            print(f"✅ Selected dataset: {current_dataset_id}")
        else:
            print(f"❌ Dataset '{dataset_input}' not found. Available datasets: {', '.join(available_datasets)}")
            continue
    
    # Main loop
    while True:
        command = input("\nEnter query or command (exit/switch <dataset_id>/datasets): ")
        
        if command.lower() == 'exit':
            break
        elif command.lower() == 'datasets':
            # Refresh dataset list
            available_datasets = list_available_datasets()
            print(f"Available datasets: {', '.join(available_datasets) if available_datasets else 'None'}")
        elif command.lower().startswith('switch '):
            try:
                new_dataset_id = command.split(' ', 1)[1].strip()
                if new_dataset_id in available_datasets:
                    print(f"🔄 Switching to dataset: {new_dataset_id}")
                    current_dataset_id = new_dataset_id
                else:
                    print(f"❌ Dataset not found: {new_dataset_id}")
                    print(f"Available datasets: {', '.join(available_datasets)}")
            except Exception as e:
                print(f"❌ Error switching dataset: {str(e)}")
        else:
            # Check query relevance
            is_relevant = check_query_relevance(command, current_dataset_id)
            print(f"\nQuery: '{command}'")
            print(f"Dataset: '{current_dataset_id}'")
            print(f"Result: {'✅ RELEVANT' if is_relevant else '❌ NOT RELEVANT'}")

# if __name__ == "__main__":
#     main()