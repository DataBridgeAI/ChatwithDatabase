import pytest
import os
import shutil
import json
import tempfile
from unittest.mock import patch, MagicMock
import chromadb
import pandas as pd

# Import the module to test
import sys
sys.modules["langchain_google_vertexai"] = MagicMock()
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from schema_embeddings_processor import extract_schema, create_embeddings, save_chromadb_to_gcs

# Use a cross-platform temp directory
TEMP_DIR = tempfile.gettempdir()
TEST_CHROMA_PATH = os.path.join(TEMP_DIR, "test_chromadb_store")
TEST_ZIP_PATH = os.path.join(TEMP_DIR, "test_chromadb_store.zip")
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
BUCKET_NAME = "bigquery-embeddings-store"
GCS_CHROMA_PATH = f"{DATASET_ID}/chromadb_store.zip"

@pytest.fixture
def mock_bigquery_client():
    """Mock BigQuery client with schema data."""
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_table.table_id = "test_table"

    # Properly mock schema fields
    mock_field1 = MagicMock()
    mock_field1.name = "column1"
    mock_field1.field_type = "STRING"

    mock_field2 = MagicMock()
    mock_field2.name = "column2"
    mock_field2.field_type = "INTEGER"

    mock_table.schema = [mock_field1, mock_field2]
    mock_client.list_tables.return_value = [mock_table]
    mock_client.get_table.return_value = mock_table
    
    with patch("google.cloud.bigquery.Client", return_value=mock_client):
        yield mock_client

def test_extract_schema(mock_bigquery_client):
    """Test extracting schema from BigQuery."""
    schema_data = extract_schema()
    
    assert len(schema_data) == 1
    assert schema_data[0]["id"] == "test_table"
    assert schema_data[0]["text"] == "column1: STRING column2: INTEGER"

@pytest.fixture
def mock_chroma_client():
    """Mock ChromaDB client."""
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    
    with patch("chromadb.PersistentClient", return_value=mock_client):
        yield mock_client, mock_collection

@pytest.fixture
def mock_vertex_embeddings():
    """Mock Vertex AI Embeddings model."""
    mock_model = MagicMock()
    mock_model.embed_documents.return_value = [[0.1, 0.2, 0.3]]
    
    with patch("schema_embeddings_processor.embedding_model", mock_model):
        yield mock_model

def test_create_embeddings(mock_chroma_client, mock_vertex_embeddings, mock_bigquery_client):
    """Test generating embeddings and storing in ChromaDB."""
    _, mock_collection = mock_chroma_client
    
    create_embeddings()
    
    mock_collection.add.assert_called_once()
    args, kwargs = mock_collection.add.call_args
    assert kwargs["ids"] == ["test_table"]
    assert "embeddings" in kwargs
    assert "metadatas" in kwargs

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
