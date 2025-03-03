import unittest
from unittest.mock import patch, MagicMock
import json
import sys
from google.cloud import bigquery, storage

import os
# Add the scripts folder to Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from schema_embedding import extract_schema, create_embeddings, save_chromadb_to_gcs

class TestSchemaEmbeddingProcessor(unittest.TestCase):

    @patch("schema_embedding_processor.bigquery.Client")
    def test_extract_schema(self, mock_bq_client):
        """Test extracting schema data from BigQuery."""
        mock_client = mock_bq_client.return_value
        mock_dataset = MagicMock()
        mock_table = MagicMock()

        # Mock BigQuery dataset and table schema
        mock_dataset_ref = MagicMock()
        mock_table.table_id = "test_table"
        mock_table.schema = [
            bigquery.SchemaField(name="id", field_type="INTEGER", mode="REQUIRED", description="Primary key"),
            bigquery.SchemaField(name="name", field_type="STRING", mode="NULLABLE", description="User name")
        ]
        mock_client.dataset.return_value = mock_dataset
        mock_client.list_tables.return_value = [mock_table]
        mock_client.get_table.return_value = mock_table

        # Call the function and assert the result
        schema_data = extract_schema(mock_client, "test_dataset")
        self.assertEqual(len(schema_data), 1)
        self.assertEqual(schema_data[0]["id"], "test_table")
        self.assertIn("id: INTEGER", schema_data[0]["text"])

    @patch("schema_embedding_processor.VertexAIEmbeddings.embed_documents")
    @patch("schema_embedding_processor.chromadb.PersistentClient")
    def test_create_embeddings(self, mock_chroma_client, mock_embed_documents):
        """Test creating embeddings for schema data."""
        mock_chroma_client_instance = mock_chroma_client.return_value
        mock_collection = MagicMock()
        mock_chroma_client_instance.get_or_create_collection.return_value = mock_collection
        
        # Mock embedding return value
        mock_embed_documents.return_value = [[0.1, 0.2, 0.3, 0.4]]
        
        schema_data = [{"id": "test_table", "text": "id: INTEGER name: STRING"}]
        
        # Call the function and assert that the embeddings are created and added to the collection
        create_embeddings(schema_data)
        mock_chroma_client_instance.get_or_create_collection.assert_called_once_with(name="RetailDataset")
        mock_collection.add.assert_called_once_with(
            ids=["test_table"],
            embeddings=[[0.1, 0.2, 0.3, 0.4]],
            metadatas=[{"text": "id: INTEGER name: STRING"}]
        )

    @patch("schema_embedding_processor.storage.Client")
    def test_save_chromadb_to_gcs(self, mock_storage_client):
        """Test saving the Chroma database to Google Cloud Storage."""
        mock_client = mock_storage_client.return_value
        mock_bucket = mock_client.bucket.return_value
        mock_blob = mock_bucket.blob.return_value

        # Simulate a successful upload to GCS
        mock_blob.upload_from_filename.return_value = None
        
        # Call the function and assert that the blob upload method is called
        save_chromadb_to_gcs()
        mock_bucket.blob.assert_called_with("RetailDataset/chromadb_store.zip")
        mock_blob.upload_from_filename.assert_called_once_with("/tmp/chromadb_store.zip")

if __name__ == "__main__":
    unittest.main()
