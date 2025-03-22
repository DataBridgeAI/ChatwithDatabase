from detoxify import Detoxify
import chromadb
from google.cloud import storage
from .bias_detector import BiasDetector
import shutil
import os

# Configuration
CHROMA_PATH = "/tmp/chromadb_store"
GCS_CHROMA_PATH = "bigquery-embeddings-store/RetailDataset/chromadb_store.zip"
LOCAL_CHROMA_ZIP_PATH = "/tmp/chromadb_store.zip"

# Initialize bias detector
bias_detector = BiasDetector()

def check_inappropriate_content(user_query):
    """Block inappropriate queries."""
    toxic_keywords = ["violence", "illegal", "fake", "prohibited"]
    
    if any(word in user_query.lower() for word in toxic_keywords):
        return "Inappropriate query detected."
    return None

def check_sql_injection(user_query):
    """Ensure SQL safety by checking for harmful SQL commands."""
    sql_blacklist = ["DROP", "DELETE", "ALTER", "INSERT", "TRUNCATE", "UPDATE"]
    
    if any(word in user_query.upper() for word in sql_blacklist):
        return "Restricted SQL operation detected."
    
    return None

def check_toxicity(query: str) -> bool:
    """Check if the query contains toxic language."""
    toxicity_score = Detoxify('original').predict(query)["toxicity"]
    return toxicity_score > 0.7

def validate_query(user_query: str) -> str:
    """Validate query for toxicity, SQL safety, and bias."""
    # Check for inappropriate content
    content_error = check_inappropriate_content(user_query)
    if content_error:
        return content_error

    # Check for SQL injection attempts
    sql_error = check_sql_injection(user_query)
    if sql_error:
        return sql_error

    # Check for bias in the query
    is_biased, bias_explanation = bias_detector.check_bias(user_query)
    if is_biased:
        return f"🚫 {bias_explanation}. Please rephrase your question to be more neutral."

    # Check for toxic content
    if check_toxicity(user_query):
        return "🚫 Query contains harmful language. Please modify your input."

    return None  # No issues detected, query is safe