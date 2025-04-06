# from google.cloud import bigquery
# import streamlit as st

# def get_bigquery_schema(project_id, dataset_id):
#     """Fetch schema details for the specified dataset in BigQuery."""
#     try:
#         client = bigquery.Client(project=project_id)
#         dataset_ref = client.dataset(dataset_id, project=project_id)
#         tables = list(client.list_tables(dataset_ref))

#         if not tables:
#             return f"No tables found in dataset `{dataset_id}`."

#         schema_info = f"BigQuery Schema for `{dataset_id}`\n"

#         for table in tables:
#             table_id = table.table_id
#             schema_info += f"\nTable: `{table_id}`\n"

#             # Fetch table schema
#             table_ref = client.get_table(f"{project_id}.{dataset_id}.{table_id}")
#             schema_info += "\nColumns:\n"

#             for field in table_ref.schema:
#                 schema_info += f"- `{field.name}` ({field.field_type})\n"

#         return schema_info
#     except Exception as error:
#         st.error(f"Schema retrieval error: {error}")
#         return None

from google.cloud import bigquery
from google.oauth2 import service_account
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

def get_bigquery_schema(project_id, dataset_id):
    """Fetch schema details for the specified dataset in BigQuery."""
    try:
        logger.info(f"Attempting to get schema for {project_id}.{dataset_id}")
        
        # Get credentials path from environment variable
        credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        logger.info(f"Using credentials from: {credentials_path}")
        
        if not credentials_path or not os.path.exists(credentials_path):
            logger.error(f"Credentials file not found at {credentials_path}")
            return None
            
        # Explicitly load credentials from file
        credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )
        
        # Create client with explicit credentials
        client = bigquery.Client(
            project=project_id,
            credentials=credentials
        )
        logger.info("BigQuery client created successfully")
        
        dataset_ref = client.dataset(dataset_id, project=project_id)
        tables = list(client.list_tables(dataset_ref))

        if not tables:
            logger.warning(f"No tables found in dataset `{dataset_id}`.")
            return f"No tables found in dataset `{dataset_id}`."

        schema_info = f"BigQuery Schema for `{dataset_id}`\n"

        for table in tables:
            table_id = table.table_id
            schema_info += f"\nTable: `{table_id}`\n"

            # Fetch table schema
            table_ref = client.get_table(f"{project_id}.{dataset_id}.{table_id}")
            schema_info += "\nColumns:\n"

            for field in table_ref.schema:
                schema_info += f"- `{field.name}` ({field.field_type})\n"

        return schema_info
    except Exception as error:
        logger.error(f"Schema retrieval error: {error}")
        import traceback
        logger.error(traceback.format_exc())
        # Re-raise the exception so it can be handled properly
        raise