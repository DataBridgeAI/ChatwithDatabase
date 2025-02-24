from google.cloud import bigquery, storage
import pickle
import os

PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "Songs"
BUCKET_NAME = "schema-embeddings-db"

bq_client = bigquery.Client(project=PROJECT_ID)
storage_client = storage.Client()

def get_current_schema():
    """Fetches current schema details from BigQuery."""
    query = f"""
    SELECT table_name, column_name, data_type 
    FROM `{PROJECT_ID}.{DATASET_ID}.INFORMATION_SCHEMA.COLUMNS`
    """
    schema_df = bq_client.query(query).to_dataframe()
    schema_info = {f"{row['table_name']}.{row['column_name']}": row['data_type'] 
                   for _, row in schema_df.iterrows()}
    return schema_info

def get_stored_schema():
    """Retrieves the last stored schema from GCS."""
    bucket = storage_client.bucket(BUCKET_NAME)
    schema_blob = bucket.blob("schema/schema_texts.pkl")
    
    if schema_blob.exists():
        schema_blob.download_to_filename("stored_schema.pkl")
        with open("stored_schema.pkl", "rb") as f:
            stored_schema = pickle.load(f)
        os.remove("stored_schema.pkl")
        return {entry.split(",")[0].split(": ")[1]: entry.split("(")[1][:-1] for entry in stored_schema}
    else:
        return {}

def detect_schema_drift():
    """Compares stored schema with current schema to detect changes."""
    stored_schema = get_stored_schema()
    current_schema = get_current_schema()

    if stored_schema == {}:
        print("No stored schema found. First-time run.")
        return True  # Trigger update

    # Detect differences
    added_columns = {col: dtype for col, dtype in current_schema.items() if col not in stored_schema}
    removed_columns = {col: dtype for col, dtype in stored_schema.items() if col not in current_schema}
    modified_columns = {col: (stored_schema[col], current_schema[col]) for col in stored_schema if col in current_schema and stored_schema[col] != current_schema[col]}

    drift_detected = bool(added_columns or removed_columns or modified_columns)

    if drift_detected:
        print("Schema drift detected!")
        print(f"Added columns: {added_columns}")
        print(f"Removed columns: {removed_columns}")
        print(f"Modified columns: {modified_columns}")
    else:
        print("No schema drift detected.")

    return drift_detected
