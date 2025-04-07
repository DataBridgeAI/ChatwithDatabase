# scripts/schema_processor.py
import json
import argparse
from google.cloud import bigquery, storage
import logging

# Use Airflow's logging system instead of writing to a file
logger = logging.getLogger("airflow.task")
logger.setLevel(logging.INFO)


def get_table_schema(client, project_id, dataset_id, table_id):
    """
    Retrieve schema for a specific BigQuery table
    """
    try:
        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        table = client.get_table(table_ref)
        
        # Extract schema information in simplified format for drift detection
        schema_fields = {field.name: field.field_type for field in table.schema}
        
        return schema_fields
    except Exception as e:
        logger.error(f"Error retrieving schema for {table_id}: {str(e)}")
        raise

def format_schema_for_prompt(schemas):
    """
    Format schema data in a way that's optimized for OpenAI prompts
    """
    prompt_schema = {}
    
    for table_id, schema in schemas.items():
        # Format column information
        columns_text = []
        for field in schema['schema']:
            description = f" - {field['description']}" if field['description'] else ""
            columns_text.append(f"{field['name']} ({field['type']}, {field['mode']}){description}")
        
        # Add formatted table information
        prompt_schema[table_id] = {
            'description': schema['description'],
            'columns': columns_text,
            'row_count': schema['num_rows']
        }
    
    # Create a markdown-formatted schema representation
    markdown_schema = "# Database Schema\n\n"
    for table, info in prompt_schema.items():
        markdown_schema += f"## Table: {table}\n\n"
        if info['description']:
            markdown_schema += f"{info['description']}\n\n"
        markdown_schema += "### Columns:\n\n"
        for column in info['columns']:
            markdown_schema += f"- {column}\n"
        markdown_schema += f"\nApproximate row count: {info['row_count']}\n\n"
    
    return markdown_schema

def upload_to_gcs(bucket_name, blob_name, content):
    """
    Upload content to Google Cloud Storage
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_string(content)
        logger.info(f"Uploaded {blob_name} to {bucket_name}")
        return True
    except Exception as e:
        logger.error(f"Error uploading to GCS: {str(e)}")
        return False

def main(project_id, dataset_id, bucket_name, output_path):
    """
    Main function to extract and process BigQuery schema
    """
    try:
        # Initialize BigQuery client
        bq_client = bigquery.Client(project=project_id)
        
        # Get all tables in the dataset
        dataset_ref = f"{project_id}.{dataset_id}"
        tables = list(bq_client.list_tables(dataset_ref))
        
        # Extract schema for each table
        schemas = {}
        for table in tables:
            table_id = table.table_id
            schema = get_table_schema(bq_client, project_id, dataset_id, table_id)
            schemas[table_id] = schema
        
        # Save raw schema data in simplified format
        all_schemas_json = json.dumps(schemas, indent=2)
        upload_to_gcs(bucket_name, f"{output_path}/all_schemas.json", all_schemas_json)
        
        logger.info(f"Successfully processed schema for {len(schemas)} tables")
        return True
    
    except Exception as e:
        logger.error(f"Error in schema processing: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process BigQuery schema for NL to SQL')
    parser.add_argument('--project_id', required=True, help='GCP Project ID')
    parser.add_argument('--dataset_id', required=True, help='BigQuery Dataset ID')
    parser.add_argument('--bucket_name', required=True, help='GCS Bucket Name')
    parser.add_argument('--output_path', default='schema_data', help='Output path in GCS bucket')
    
    args = parser.parse_args()
    main(args.project_id, args.dataset_id, args.bucket_name, args.output_path)
