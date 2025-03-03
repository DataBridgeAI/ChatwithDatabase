import unittest
from unittest.mock import patch, MagicMock
import json
import shutil
from google.cloud import bigquery, storage
import sys
import os

# Add the scripts folder to Python's path for module import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from schema_embedding import extract_schema, create_embeddings, save_chromadb_to_gcs

class TestSchemaEmbeddingProcessor(unittest.TestCase):

    @patch("schema_embedding.bigquery.Client")
    def test_extract_schema(self, mock_bq_client):
        """Test extracting schema data from BigQuery."""

        # Mock BigQuery client and dataset/table
        mock_client = mock_bq_client.return_value
        mock_dataset = MagicMock()
        mock_table = MagicMock()
        
        # Simulate BigQuery dataset and table schema
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
        
        # Validate extracted schema
        self.assertEqual(len(schema_data), 1)
        self.assertEqual(schema_data[0]["id"], "test_table")
        self.assertIn("id: INTEGER", schema_data[0]["text"])
        self.assertIn("name: STRING", schema_data[0]["text"])

    @patch("schema_embedding.chromadb.PersistentClient")
    @patch("schema_embedding.VertexAIEmbeddings.embed_documents")
    def test_create_embeddings(self, mock_embed_documents, mock_chroma_client):
        """Test creating embeddings for schema data."""

        # Mock Chroma client and collection
        mock_chroma_client_instance = mock_chroma_client.return_value
        mock_collection = MagicMock()
        mock_chroma_client_instance.get_or_create_collection.return_value = mock_collection
        
        # Mock embedding return value
        mock_embed_documents.return_value = [[0.1, 0.2, 0.3, 0.4]]
        
        # Test data (schema text)
        schema_data = [{"id": "test_table", "text": "id: INTEGER name: STRING"}]
        
        # Call the function
        create_embeddings(schema_data)
        
        # Ensure the collection was created and embeddings were added
        mock_chroma_client_instance.get_or_create_collection.assert_called_once_with(name="RetailDataset")
        mock_collection.add.assert_called_once_with(
            ids=["test_table"],
            embeddings=[[0.1, 0.2, 0.3, 0.4]],
            metadatas=[{"text": "id: INTEGER name: STRING"}]
        )

# class TestSchemaEmbeddingProcessor(unittest.TestCase):

#     @patch("scripts.schema_embedding.shutil.make_archive")  # Mock make_archive to avoid actual file creation
#     @patch("scripts.schema_embedding.storage.Client")  # Mock the GCS Client
#     def test_save_chromadb_to_gcs(self, mock_storage_client, mock_make_archive):
#         """Test saving the Chroma database to Google Cloud Storage."""

#         # Mock the GCS client and bucket
#         mock_client = MagicMock()
#         mock_bucket = MagicMock()
#         mock_blob = MagicMock()

#         # Set up the mock objects
#         mock_storage_client.return_value = mock_client
#         mock_client.bucket.return_value = mock_bucket
#         mock_bucket.blob.return_value = mock_blob

#         # Simulate the behavior of blob.upload_from_filename (no actual file is uploaded)
#         mock_blob.upload_from_filename.return_value = None  # Simulate a successful upload

#         # Create a temporary directory using tempfile for cross-platform compatibility
#         with patch("scripts.schema_embedding.tempfile.TemporaryDirectory") as mock_tmpdir:
#             mock_tmpdir.return_value = "C:\\Users\\mansi\\AppData\\Local\\Temp\\tmp_testdir"  # Simulate temp directory path for Windows

#             # Call the function under test
#             save_chromadb_to_gcs()

#             # Check if the mock methods were called as expected
#             mock_storage_client.assert_called_once()  # Check if the GCS client was created
#             mock_client.bucket.assert_called_once_with("bigquery-embeddings-store")  # Check if the correct bucket was accessed
#             mock_bucket.blob.assert_called_once_with("RetailDataset/chromadb_store.zip")  # Check if the correct blob was created
#             mock_blob.upload_from_filename.assert_called_once_with("C:\\Users\\mansi\\AppData\\Local\\Temp\\tmp_testdir\\chromadb_store.zip")  # Check if the file upload was called with the correct path
#             mock_make_archive.assert_called_once_with("C:\\Users\\mansi\\AppData\\Local\\Temp\\tmp_testdir", 'zip', "/tmp/chromadb_store")  # Ensure make_archive was called with correct arguments

# if __name__ == "__main__":
#     unittest.main()


    # @patch("schema_embedding.storage.Client")
    # def test_save_chromadb_to_gcs(self, mock_storage_client):
    #     """Test saving the Chroma database to Google Cloud Storage."""

    #     # Mock GCS client and blob
    #     mock_client = mock_storage_client.return_value
    #     mock_bucket = mock_client.bucket.return_value
    #     mock_blob = mock_bucket.blob.return_value
        
    #     # Simulate a successful upload to GCS
    #     mock_blob.upload_from_filename.return_value = None
        
    #     # Call the function to save Chroma DB
    #     save_chromadb_to_gcs()
        
    #     # Validate the blob upload method was called with the correct file path
    #     mock_bucket.blob.assert_called_with("RetailDataset/chromadb_store.zip")
    #     mock_blob.upload_from_filename.assert_called_once_with("/tmp/chromadb_store.zip")

if __name__ == "__main__":
    unittest.main()
