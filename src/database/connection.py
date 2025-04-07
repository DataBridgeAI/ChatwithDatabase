import os
from google.cloud import bigquery

def get_bigquery_client():
    """Initialize Google BigQuery client using service account credentials."""
    
    # Ensure authentication key is set
    json_key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not json_key_path or not os.path.exists(json_key_path):
        raise FileNotFoundError(f"Service account key file not found: {json_key_path}")

    # Initialize BigQuery client
    return bigquery.Client()
