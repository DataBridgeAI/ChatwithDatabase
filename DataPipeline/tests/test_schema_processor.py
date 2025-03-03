import unittest
from unittest.mock import patch, MagicMock
import json
import sys
from google.cloud import bigquery  # Import actual BigQuery schema classes

import os
# Add the scripts folder to Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from schema_processor import get_table_schema, format_schema_for_prompt, upload_to_gcs, main

class TestSchemaProcessor(unittest.TestCase):

    @patch("schema_processor.bigquery.Client")
    def test_get_table_schema(self, mock_bq_client):
        """Test retrieving schema from BigQuery."""
        mock_client = mock_bq_client.return_value
        mock_table = MagicMock()
       
        mock_table.schema = [
            bigquery.SchemaField(name="id", field_type="INTEGER", mode="REQUIRED", description="Primary key"),
            bigquery.SchemaField(name="name", field_type="STRING", mode="NULLABLE", description="User name")
        ]

        mock_table.num_rows = 100
        mock_table.description = "User data table"
        mock_table.created = None
        mock_table.modified = None
        mock_client.get_table.return_value = mock_table

        schema = get_table_schema(mock_client, "test_project", "test_dataset", "test_table")

        self.assertEqual(schema["table_id"], "test_table")
        self.assertEqual(schema["schema"][0]["name"], "id")
        self.assertEqual(schema["num_rows"], 100)

    def test_format_schema_for_prompt(self):
        """Test formatting schema for prompts."""
        schemas = {
            "users": {
                "description": "User details",
                "num_rows": 500,
                "schema": [
                    {"name": "id", "type": "INTEGER", "mode": "REQUIRED", "description": "Primary key"},
                    {"name": "email", "type": "STRING", "mode": "NULLABLE", "description": "User email"}
                ]
            }
        }

        formatted_schema = format_schema_for_prompt(schemas)

        self.assertIn("## Table: users", formatted_schema)
        self.assertIn("id (INTEGER, REQUIRED) - Primary key", formatted_schema)
        self.assertIn("Approximate row count: 500", formatted_schema)

    @patch("schema_processor.storage.Client")
    def test_upload_to_gcs(self, mock_storage_client):
        """Test uploading to GCS."""
        mock_client = mock_storage_client.return_value
        mock_bucket = mock_client.bucket.return_value
        mock_blob = mock_bucket.blob.return_value

        success = upload_to_gcs("test_bucket", "test_path/file.json", "{}")

        mock_bucket.blob.assert_called_with("test_path/file.json")
        mock_blob.upload_from_string.assert_called_once()
        self.assertTrue(success)

    @patch("schema_processor.bigquery.Client")
    @patch("schema_processor.storage.Client")
    def test_main(self, mock_storage_client, mock_bq_client):
        """Test the main function with mocks."""
        mock_client = mock_bq_client.return_value
        mock_storage = mock_storage_client.return_value

        # Mock BigQuery table
        mock_table = MagicMock()
        mock_table.table_id = "users"
        mock_client.list_tables.return_value = [mock_table]

        # Mock schema retrieval
        mock_client.get_table.return_value = MagicMock(
            schema=[
                bigquery.SchemaField(name="id", field_type="INTEGER", mode="REQUIRED", description="Primary key"),
                bigquery.SchemaField(name="name", field_type="STRING", mode="NULLABLE", description="User name")
            ],
            num_rows=100,
            description="User data table",
            created=None,
            modified=None
        )

        # Mock GCS upload success
        mock_storage.bucket.return_value.blob.return_value.upload_from_string.return_value = None

        # Run the function
        success = main("test_project", "test_dataset", "test_bucket", "output_path")
        
        # Assert success
        self.assertTrue(success)

if __name__ == "__main__":
    unittest.main()
