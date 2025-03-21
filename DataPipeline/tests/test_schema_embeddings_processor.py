import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

# Import the module to test
import sys
sys.modules["langchain_google_vertexai"] = MagicMock()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from schema_embeddings_processor import extract_schema, generate_schema_embeddings, upload_embeddings_to_gcs

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

def test_extract_schema(mock_bigquery_client):
    """Test extracting schema from BigQuery."""
    schema_data = extract_schema()

    # Adjust assertions to reflect updated mock data
    assert len(schema_data) == 2
    assert schema_data[0]["table"] == "test_table"
    assert schema_data[0]["column"] == "column1"
    assert "STRING" in schema_data[0]["semantic_text"]

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

def test_create_embeddings(mock_vertex_embeddings, mock_bigquery_client):
    """Test generating embeddings and storing in JSON."""
    generate_schema_embeddings()

    # Ensure embedding model is called
    mock_vertex_embeddings.embed_documents.assert_called_once()

    # Validate schema embeddings creation
    args, _ = mock_vertex_embeddings.embed_documents.call_args
    assert len(args[0]) == 2  # Two semantic texts
