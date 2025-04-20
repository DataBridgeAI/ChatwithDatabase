import os
import json
import numpy as np
from google.cloud import storage
from langchain_google_vertexai import VertexAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache
import re
from typing import Dict, List, Tuple, Any, Optional
import chromadb
from chromadb.config import Settings

from rapidfuzz import fuzz, process

# Configuration Parameters
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
VERTEX_MODEL = "textembedding-gecko@003"
BUCKET_NAME = "bigquery-embeddings-store"
EMBEDDINGS_FILE = "schema_embeddings.json"

# Create embeddings directory if it doesn't exist
EMBEDDINGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'embeddings')
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
LOCAL_EMBEDDINGS_PATH = os.path.join(EMBEDDINGS_DIR, EMBEDDINGS_FILE)
CHROMA_PERSIST_DIR = os.path.join(EMBEDDINGS_DIR, 'chroma')

# Initialize Vertex AI Embeddings
embedding_model = VertexAIEmbeddings(model=VERTEX_MODEL)
gcs_client = storage.Client()

def preprocess_text(text: str) -> str:
    """
    Preprocess text for better matching:
    1. Convert to lowercase
    2. Remove special characters (except spaces)
    3. Normalize whitespace
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep spaces between words
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def setup_chroma_client() -> chromadb.PersistentClient:
    """
    Set up and return a ChromaDB client
    """
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    return client

def initialize_vector_db(schema_embeddings: Dict[str, Any]) -> chromadb.Collection:
    """
    Initialize or update the vector database with schema embeddings
    """
    client = setup_chroma_client()
    
    # Remove existing collection if it exists
    try:
        client.delete_collection("schema_embeddings")
    except:
        pass
    
    # Create a new collection
    collection = client.create_collection(
        name="schema_embeddings",
        metadata={"description": "Schema embeddings for semantic search"}
    )
    
    # Prepare data for batch insertion
    ids = []
    embeddings = []
    metadatas = []
    documents = []
    
    for key, value in schema_embeddings.items():
        ids.append(key)
        embeddings.append(value["embedding"])
        table, column = key.split(":")
        metadatas.append({
            "table": table,
            "column": column,
            "full_key": key
        })
        documents.append(value["semantic_text"])
    
    # Add embeddings to the collection
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents
    )
    
    return collection

@lru_cache(maxsize=1)
def get_vector_db() -> chromadb.Collection:
    """
    Get or create the vector database collection
    Cached to prevent multiple initializations
    """
    client = setup_chroma_client()
    try:
        collection = client.get_collection("schema_embeddings")
        return collection
    except:
        # Collection doesn't exist, need to initialize it
        schema_embeddings = download_and_prepare_embeddings()
        return initialize_vector_db(schema_embeddings)

@lru_cache(maxsize=1)
def download_and_prepare_embeddings():
    """
    Downloads schema embeddings from GCS and prepares them for search.
    Returns a dictionary of prepared embeddings.
    Cached to prevent multiple downloads.
    """
    try:
        # Step 1: Download from GCS if not exists locally
        if not os.path.exists(LOCAL_EMBEDDINGS_PATH):
            print("📥 Downloading schema embeddings from GCS...")
            bucket = gcs_client.bucket(BUCKET_NAME)
            blob = bucket.blob(EMBEDDINGS_FILE)
            blob.download_to_filename(LOCAL_EMBEDDINGS_PATH)
        
        # Step 2: Load and prepare embeddings
        with open(LOCAL_EMBEDDINGS_PATH, 'r') as f:
            schema_data = json.load(f)
        
        # Step 3: Convert embeddings to numpy arrays for faster comparison
        prepared_embeddings = {}
        for key, value in schema_data.items():
            prepared_embeddings[key] = {
                'embedding': np.array(value['embedding']),
                'semantic_text': value['semantic_text']
            }
        
        return prepared_embeddings
        
    except Exception as e:
        print(f"❌ Error preparing embeddings: {str(e)}")
        return None

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

def check_query_relevance(user_input: str, schema_embeddings: Optional[Dict[str, Any]] = None, threshold: float = 0.70) -> bool:
    """
    Check if the user query is relevant to the schema and return a boolean result.
    Returns:
        bool: True if query is relevant, False otherwise
    """
    try:
        # Step 1: Preprocess input
        processed_input = preprocess_text(user_input)
        
        # Step 2: Get schema information
        if schema_embeddings is None:
            schema_embeddings = download_and_prepare_embeddings()
        if not schema_embeddings:
            print("❌ Could not load schema embeddings")
            return True  # Default to true in case of errors
        
        schema_keys = list(schema_embeddings.keys())
        
        # Step 3-8: Process and analyze query
        schema_terms = extract_potential_schema_terms(user_input)
        fuzzy_matches = find_fuzzy_matches(schema_keys, schema_terms)
        query_embedding = generate_user_input_embedding(processed_input)
        
        vector_db = get_vector_db()
        results = vector_db.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=5
        )
        
        # Process semantic matches
        semantic_matches = []
        for i, (doc_id, distance) in enumerate(zip(results['ids'][0], results['distances'][0])):
            similarity = 1.0 - distance
            semantic_matches.append({
                "schema_element": doc_id,
                "similarity": similarity,
                "semantic_text": results['documents'][0][i],
                "matched_on": "semantic"
            })
        
        # Combine and process matches
        all_matches = []
        all_matches.extend([{
            "schema_element": match["schema_element"],
            "score": match["similarity"],
            "match_type": "semantic",
            "matched_on": "semantic",
            "semantic_text": match["semantic_text"]
        } for match in semantic_matches])
        
        for match in fuzzy_matches:
            all_matches.append({
                "schema_element": match["schema_element"],
                "score": match["match_score"] * 0.9,
                "match_type": "fuzzy",
                "matched_on": match["matched_on"],
                "matched_term": match["matched_term"],
                "semantic_text": schema_embeddings[match["schema_element"]]["semantic_text"]
            })
        
        # Merge and sort matches
        unique_matches = {}
        for match in all_matches:
            key = match["schema_element"]
            if key not in unique_matches or match["score"] > unique_matches[key]["score"]:
                unique_matches[key] = match
        
        top_matches = sorted(list(unique_matches.values()), key=lambda x: x["score"], reverse=True)
        
        # Calculate final score
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
        
        is_relevant = combined_score >= threshold
        if not is_relevant:
            print(f"❌ Query is NOT RELEVANT to the schema (Score: {combined_score:.2f})")
        
        return is_relevant
        
    except Exception as e:
        print(f"❌ Error checking query relevance: {str(e)}")
        return True  # Default to true in case of errors

if __name__ == "__main__":
    print("\n🔍 Schema-Agnostic Query Relevance Checker")
    print("Type 'exit' to quit\n")
    
    while True:
        user_input = input("Enter your query: ")
        if user_input.lower() == 'exit':
            break
            
        is_relevant = check_query_relevance(user_input)
        print("✅ Query is RELEVANT" if is_relevant else "❌ Query is NOT RELEVANT")
        print()