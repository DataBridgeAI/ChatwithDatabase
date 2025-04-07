import os
import json
import numpy as np
from google.cloud import bigquery, storage
from langchain_google_vertexai import VertexAIEmbeddings
from typing import Dict, List, Any, Optional
import chromadb
from chromadb.config import Settings
import shutil

# Configuration Parameters
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
VERTEX_MODEL = "textembedding-gecko@003"
BUCKET_NAME = "bigquery-embeddings-store"
#EMBEDDINGS_FILE = "schema_embeddings.json"
#LOCAL_EMBEDDINGS_PATH = f"/tmp/{EMBEDDINGS_FILE}"

GCS_PERSIST_PATH = "chroma_db/"
ZIP_FILE_PATH = "./schema_chroma.zip"
LOCAL_PERSIST_PATH = "./schema_chroma/"
ZIP_FILE_PATH = "./schema_chroma.zip"
GCS_ZIP_PATH = "chroma_db/schema_chroma.zip"


# # Create embeddings directory if it doesn't exist
# EMBEDDINGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'embeddings')
# os.makedirs(EMBEDDINGS_DIR, exist_ok=True)
# CHROMA_PERSIST_DIR = os.path.join(EMBEDDINGS_DIR, 'chroma')

# Initialize Vertex AI Embeddings
storage_client = storage.Client()
embedding_model = VertexAIEmbeddings(model=VERTEX_MODEL)

# Ensure the local directory exists
os.makedirs(LOCAL_PERSIST_PATH, exist_ok=True)


def zip_directory():
    """Zip the ChromaDB directory."""
    shutil.make_archive(ZIP_FILE_PATH.replace(".zip", ""), 'zip', LOCAL_PERSIST_PATH)
    print(f"Zipped directory {LOCAL_PERSIST_PATH} to {ZIP_FILE_PATH}")

def upload_zip_to_gcs():
    """Upload zipped embeddings to Google Cloud Storage."""
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(GCS_ZIP_PATH)
    blob.upload_from_filename(ZIP_FILE_PATH)
    print(f"Uploaded {ZIP_FILE_PATH} to gs://{BUCKET_NAME}/{GCS_ZIP_PATH}")


def extract_schema():
    """
    Extract schema details with rich context information.
    This method is schema-agnostic and doesn't make assumptions about column names.
    """
    client = bigquery.Client(project=PROJECT_ID)
    dataset_ref = client.dataset(DATASET_ID)
    tables = client.list_tables(dataset_ref)

    schema_data = []
    for table in tables:
        table_ref = dataset_ref.table(table.table_id)
        table_obj = client.get_table(table_ref)
        table_schema = table_obj.schema
        
        print(f"Processing table: {table.table_id}")

        # Get table description if available
        table_desc = table_obj.description or f"A table named {table.table_id}"

        # Create rich table context
        table_context = create_table_context(client, table.table_id, table_obj)

        for field in table_schema:
            # Get column statistics and sample values
            column_stats = get_column_statistics(client, DATASET_ID, table.table_id, field.name, field.field_type)
            sample_values = get_sample_values(client, DATASET_ID, table.table_id, field.name)
            
            # Create semantic text using available data without assumptions
            semantic_text = create_column_semantic_text(
                table.table_id,
                field.name,
                field.field_type,
                field.description,
                table_desc,
                column_stats,
                sample_values,
                table_context
            )
            
            schema_data.append({
                "table": table.table_id,
                "column": field.name,
                "data_type": field.field_type,
                "semantic_text": semantic_text
            })
    
    return schema_data

def create_table_context(client, table_id, table_obj):
    """
    Create rich context about a table by analyzing its structure and relationships.
    """
    context = {}
    
    try:
        # Get row count (approx)
        query = f"""
            SELECT COUNT(*) as row_count
            FROM {PROJECT_ID}.{DATASET_ID}.{table_id}
        """
        row_count_job = client.query(query)
        row_count_result = row_count_job.result()
        for row in row_count_result:
            context["row_count"] = row.row_count
        
        # Get column count
        context["column_count"] = len(table_obj.schema)
        
        # Check for potential primary keys
        # Look for columns that might be primary keys (unique, not null)
        for field in table_obj.schema:
            if field.name.lower().endswith('id') or field.name.lower() == 'id':
                query = f"""
                    SELECT 
                        COUNT(*) as total_count,
                        COUNT(DISTINCT {field.name}) as distinct_count
                    FROM {PROJECT_ID}.{DATASET_ID}.{table_id}
                    WHERE {field.name} IS NOT NULL
                """
                pk_check_job = client.query(query)
                pk_check_result = pk_check_job.result()
                
                for row in pk_check_result:
                    if row.total_count > 0 and row.total_count == row.distinct_count:
                        if "potential_primary_keys" not in context:
                            context["potential_primary_keys"] = []
                        context["potential_primary_keys"].append(field.name)
                
        # Detect potential foreign key relationships
        for field in table_obj.schema:
            if field.name.lower().endswith('_id'):
                # Extract potential referenced table name
                potential_table = field.name.lower().replace('_id', '')
                
                # Check if this table exists in the dataset
                tables = [t.table_id for t in client.list_tables(client.dataset(DATASET_ID))]
                
                if potential_table in [t.lower() for t in tables]:
                    if "potential_foreign_keys" not in context:
                        context["potential_foreign_keys"] = []
                    context["potential_foreign_keys"].append({
                        "column": field.name,
                        "references_table": potential_table
                    })
        
    except Exception as e:
        print(f"Error creating table context for {table_id}: {str(e)}")
    
    return context

def get_column_statistics(client, dataset_id, table_id, column_name, data_type):
    """
    Get statistics for a column to enhance semantic understanding.
    """
    stats = {}
    
    try:
        # Count distinct values
        query = f"""
            SELECT COUNT(DISTINCT {column_name}) as distinct_count
            FROM {PROJECT_ID}.{dataset_id}.{table_id}
        """
        result = client.query(query).result()
        for row in result:
            stats['distinct_count'] = row.distinct_count
        
        # Calculate null percentage
        query = f"""
            SELECT 
                COUNTIF({column_name} IS NULL) * 100.0 / COUNT(*) as null_percentage
            FROM {PROJECT_ID}.{dataset_id}.{table_id}
        """
        result = client.query(query).result()
        for row in result:
            stats['null_percentage'] = row.null_percentage
        
        # Get min and max for numeric or date columns
        if data_type in ['INTEGER', 'FLOAT', 'NUMERIC', 'TIMESTAMP', 'DATE']:
            query = f"""
                SELECT 
                    MIN({column_name}) as min_val,
                    MAX({column_name}) as max_val
                FROM {PROJECT_ID}.{dataset_id}.{table_id}
            """
            result = client.query(query).result()
            for row in result:
                stats['min'] = row.min_val
                stats['max'] = row.max_val
        
        return stats
    except Exception as e:
        print(f"Error getting statistics for {table_id}.{column_name}: {str(e)}")
        return stats

def get_sample_values(client, dataset_id, table_id, column_name):
    """
    Get sample values for a column to enhance semantic understanding.
    """
    samples = []
    
    try:
        # Get a few sample values
        query = f"""
            SELECT DISTINCT {column_name}
            FROM {PROJECT_ID}.{dataset_id}.{table_id}
            WHERE {column_name} IS NOT NULL
            LIMIT 5
        """
        result = client.query(query).result()
        for row in result:
            samples.append(getattr(row, column_name))
        
        return samples
    except Exception as e:
        print(f"Error getting sample values for {table_id}.{column_name}: {str(e)}")
        return samples

def create_column_semantic_text(
    table_id, 
    column_name, 
    data_type, 
    column_description, 
    table_description, 
    column_stats, 
    sample_values,
    table_context
):
    """
    Create rich semantic text for a column using available data without making assumptions.
    """
    # Start with basic information
    semantic_text = f"Column '{column_name}' in table '{table_id}' with data type {data_type}."
    
    # Add column description if available
    if column_description:
        semantic_text += f" Column description: {column_description}."
    
    # Add table description if available
    if table_description:
        semantic_text += f" This column is part of a table that {table_description}."
    
    # Add statistical information
    if column_stats:
        if 'distinct_count' in column_stats:
            if column_stats['distinct_count'] == 1:
                semantic_text += f" This column has only one unique value."
            else:
                semantic_text += f" This column has {column_stats['distinct_count']} distinct values."
                
        if 'null_percentage' in column_stats and column_stats['null_percentage'] > 0:
            semantic_text += f" About {column_stats['null_percentage']:.1f}% of values are null."
            
        if 'min' in column_stats and 'max' in column_stats:
            if isinstance(column_stats['min'], (int, float)) and isinstance(column_stats['max'], (int, float)):
                semantic_text += f" Values range from {column_stats['min']} to {column_stats['max']}."
    
    # Add sample value information
    if sample_values and len(sample_values) > 0:
        cleaned_samples = [str(s) for s in sample_values if s is not None]
        if cleaned_samples:
            semantic_text += f" Sample values include: {', '.join(cleaned_samples[:3])}."
    
    # Add schema relationship context
    if table_context:
        # Check if this might be a primary key
        if "potential_primary_keys" in table_context and column_name in table_context["potential_primary_keys"]:
            semantic_text += f" This column appears to be a unique identifier (potential primary key)."
        
        # Check if this might be a foreign key
        if "potential_foreign_keys" in table_context:
            for fk in table_context["potential_foreign_keys"]:
                if fk["column"] == column_name:
                    semantic_text += f" This column appears to reference the {fk['references_table']} table."
    
    return semantic_text

def generate_schema_embeddings():
    """Generate embeddings for schema data."""
    schema_data = extract_schema()
    
    # Create schema texts with standard descriptions
    schema_texts = [item["semantic_text"] for item in schema_data]
    
    # Create embeddings for semantic descriptions
    schema_embeddings = embedding_model.embed_documents(schema_texts)
    
    schema_dict = {}
    for idx, item in enumerate(schema_data):
        key = f"{item['table']}:{item['column']}"
        schema_dict[key] = {
            'embedding': schema_embeddings[idx],
            'semantic_text': item['semantic_text'],
            'data_type': item['data_type']
        }
    
    print(f"Generated {len(schema_texts)} schema embeddings")
    return schema_dict

def initialize_vector_db(schema_embeddings: Dict[str, Any]) -> chromadb.Collection:
    """Initialize ChromaDB with schema embeddings and store both locally and in GCS."""
    # Create ChromaDB client with local persistence
    chroma_client = chromadb.PersistentClient(path=LOCAL_PERSIST_PATH)
    
    # Create or get collection
    collection = chroma_client.get_or_create_collection(
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
            "data_type": value.get("data_type", "unknown")
        })
        documents.append(value["semantic_text"])
    
    # Add embeddings to the collection
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents
    )
    
    print(f"✅ Added {len(ids)} embeddings to ChromaDB")
    
    # Zip the local ChromaDB directory
    zip_directory()
    
    # Upload to GCS
    upload_zip_to_gcs()
    
    return collection

def generate_and_store_embeddings():
    """Main function to orchestrate the embeddings generation and storage process."""
    try:
        print("\n🔄 Starting schema embeddings generation process...")
        
        # Generate embeddings
        schema_embeddings = generate_schema_embeddings()
        
        # Initialize ChromaDB and store it (both locally and in GCS)
        initialize_vector_db(schema_embeddings)
        
        print("\n✅ Schema embeddings generation and storage process completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error in embeddings generation process: {str(e)}")
        return False

if __name__ == "__main__":
    # Run the process
    generate_and_store_embeddings()
