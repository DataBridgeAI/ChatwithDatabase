import os
import shutil
import pytest
from unittest import mock
from unittest.mock import MagicMock
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

from feedback_helper import (
    zip_directory, upload_zip_to_gcs, generate_query_embeddings,
    fetch_user_queries, store_embeddings_gcs
)

@pytest.fixture
def mock_gcs_client():
    with mock.patch("feedback_helper.storage.Client") as mock_storage_client:
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        yield mock_blob

@pytest.fixture
def mock_bigquery_client():
    with mock.patch("feedback_helper.bigquery.Client") as mock_bigquery_client:
        mock_query_job = MagicMock()
        mock_query_job.result.return_value = [
            MagicMock(user_question="What is AI?", generated_sql="SELECT * FROM ai", feedback='1')
        ]
        mock_bigquery_client.return_value.query.return_value = mock_query_job
        yield mock_bigquery_client

@mock.patch("feedback_helper.shutil.make_archive")
def test_zip_directory(mock_make_archive):
    zip_directory()
    mock_make_archive.assert_called_once()

@mock.patch("feedback_helper.os.path.exists", return_value=True)
@mock.patch("feedback_helper.PersistentClient")
@mock.patch("feedback_helper.open", new_callable=mock.mock_open, read_data="What is AI?||SELECT * FROM ai||1")
def test_generate_query_embeddings(mock_open, mock_persistent_client, mock_path_exists):
    mock_collection = MagicMock()
    mock_persistent_client.return_value.get_or_create_collection.return_value = mock_collection
    
    generate_query_embeddings()
    mock_collection.add.assert_called_once()

@mock.patch("feedback_helper.open", new_callable=mock.mock_open)
def test_fetch_user_queries(mock_open, mock_bigquery_client):
    queries = fetch_user_queries()
    assert len(queries) == 1
    assert queries[0] == ("What is AI?", "SELECT * FROM ai", '1')

@mock.patch("feedback_helper.PersistentClient")
def test_store_embeddings_gcs(mock_persistent_client):
    mock_collection = MagicMock()
    mock_persistent_client.return_value.get_or_create_collection.return_value = mock_collection
    
    store_embeddings_gcs("What is AI?", [0.1, 0.2, 0.3], "SELECT * FROM ai", '1')
    mock_collection.add.assert_called_once()

