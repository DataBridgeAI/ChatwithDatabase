import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

# Import the module to test
import sys
sys.modules["langchain_google_vertexai"] = MagicMock()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

# Import constants from schema_embeddings_processor
from schema_embeddings_processor import (
    extract_schema, 
    generate_schema_embeddings, 
    upload_zip_to_gcs,
    ZIP_FILE_PATH,
    GCS_ZIP_PATH
)

# Cross-platform temp directory
TEMP_DIR = tempfile.gettempdir()

@pytest.fixture
def mock_bigquery_client():
    """Mock BigQuery client with schema data."""
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_table.table_id = "test_table"
    mock_table.description = "Test table description"

    # Mock schema fields
    mock_field1 = MagicMock()
    mock_field1.name = "column1"
    mock_field1.field_type = "STRING"
    mock_field1.description = "stores string values"

    mock_field2 = MagicMock()
    mock_field2.name = "column2"
    mock_field2.field_type = "INTEGER"
    mock_field2.description = "stores integer values"

    mock_table.schema = [mock_field1, mock_field2]
    mock_client.list_tables.return_value = [mock_table]
    mock_client.get_table.return_value = mock_table

    with patch("google.cloud.bigquery.Client", return_value=mock_client):
        yield mock_client

@pytest.fixture
def mock_storage_client():
    """Mock GCS storage client."""
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()

    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    with patch("google.cloud.storage.Client", return_value=mock_client):
        yield mock_client, mock_blob

@pytest.fixture
def mock_vertex_embeddings():
    """Mock Vertex AI Embeddings model."""
    mock_model = MagicMock()
    mock_model.embed_documents.return_value = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6]
    ]

    with patch("schema_embeddings_processor.embedding_model", mock_model):
        yield mock_model

def test_extract_schema(mock_bigquery_client):
    """Test extracting schema from BigQuery."""
    schema_data = extract_schema()

    assert len(schema_data) == 2
    assert schema_data[0]["table"] == "test_table"
    assert schema_data[0]["column"] == "column1"
    assert "STRING" in schema_data[0]["semantic_text"]

def test_create_embeddings(mock_vertex_embeddings, mock_bigquery_client):
    """Test generating embeddings and storing in JSON."""
    generate_schema_embeddings()

    mock_vertex_embeddings.embed_documents.assert_called_once()
    args, _ = mock_vertex_embeddings.embed_documents.call_args
    assert len(args[0]) == 2  # Two semantic texts

def test_upload_embeddings(mock_storage_client):
    """Test uploading embeddings to GCS."""
    mock_client, mock_blob = mock_storage_client

    # Create a temporary directory structure
    os.makedirs(os.path.dirname(ZIP_FILE_PATH), exist_ok=True)
    
    # Create a dummy zip file
    with open(ZIP_FILE_PATH, 'w') as f:
        f.write("dummy content")

    # Patch the bucket name and storage client
    with patch("schema_embeddings_processor.BUCKET_NAME", "test-bucket"), \
         patch("schema_embeddings_processor.storage_client", mock_client):

        # Call the function under test
        upload_zip_to_gcs()

        # Verify the correct bucket was accessed
        mock_client.bucket.assert_called_once_with("test-bucket")
        
        # Verify the correct blob path was used
        mock_bucket = mock_client.bucket.return_value
        mock_bucket.blob.assert_called_once_with(GCS_ZIP_PATH)
        
        # Verify the upload was called with the correct file
        mock_blob.upload_from_filename.assert_called_once_with(ZIP_FILE_PATH)

    # Cleanup
    if os.path.exists(ZIP_FILE_PATH):
        os.remove(ZIP_FILE_PATH)
