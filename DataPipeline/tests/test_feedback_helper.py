import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
import pytest
from unittest.mock import patch, MagicMock, mock_open

import feedback_helper


@patch("feedback_helper.shutil.make_archive")
@patch("feedback_helper.print")
def test_zip_directory(mock_print, mock_make_archive):
    feedback_helper.zip_directory()
    mock_make_archive.assert_called_once()
    mock_print.assert_called_once()


@patch("feedback_helper.storage_client")
@patch("feedback_helper.print")
def test_upload_zip_to_gcs(mock_print, mock_storage_client):
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_storage_client.bucket.return_value = mock_bucket  # No .return_value after mock_storage_client

    feedback_helper.upload_zip_to_gcs()

    mock_blob.upload_from_filename.assert_called_once()


@patch("feedback_helper.bigquery.Client")
def test_fetch_user_queries(mock_bigquery_client):
    mock_result = MagicMock()
    mock_row = MagicMock(user_question="question", generated_sql="sql", feedback="1")
    mock_result.__iter__.return_value = [mock_row]
    mock_bigquery_client.return_value.query.return_value.result.return_value = mock_result

    queries = feedback_helper.fetch_user_queries(hours=24)
    assert queries == [("question", "sql", "1")]


@patch("feedback_helper.zipfile.ZipFile")
@patch("feedback_helper.os.path.exists", return_value=True)
@patch("feedback_helper.storage_client")
@patch("feedback_helper.print")
def test_download_existing_embeddings(mock_print, mock_storage_client, mock_exists, mock_zipfile):
    mock_bucket = MagicMock()
    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob
    mock_storage_client.bucket.return_value = mock_bucket  # No .return_value here either

    feedback_helper.download_existing_embeddings()

    mock_blob.download_to_filename.assert_called_once()




@patch("feedback_helper.get_embedding_model")
@patch("feedback_helper.download_existing_embeddings")
@patch("feedback_helper.PersistentClient")
@patch("feedback_helper.print")
def test_update_query_embeddings_add_new(mock_print, mock_chroma_client, mock_download, mock_get_model):
    mock_model = MagicMock()
    mock_model.encode.return_value = [0.1] * 384
    mock_get_model.return_value = mock_model

    mock_collection = MagicMock()
    mock_collection.get.return_value = {'ids': []}
    mock_client_instance = MagicMock()
    mock_client_instance.get_or_create_collection.return_value = mock_collection
    mock_chroma_client.return_value = mock_client_instance

    queries = [("new query", "SELECT *", "1")]
    feedback_helper.update_query_embeddings(queries)

    mock_download.assert_called_once()
    mock_get_model.assert_called_once()
    mock_collection.add.assert_called_once()
    mock_print.assert_any_call("Added new embedding for query: new query...")


@patch("feedback_helper.print")
def test_update_query_embeddings_empty(mock_print):
    feedback_helper.update_query_embeddings([])
    mock_print.assert_called_with("No new queries found. Skipping embedding generation.")


@patch("feedback_helper.SentenceTransformer")
def test_get_embedding_model_threadsafe(mock_sentence_transformer):
    mock_model_instance = MagicMock()
    mock_sentence_transformer.return_value = mock_model_instance

    # Force re-init model
    feedback_helper._model = None

    model = feedback_helper.get_embedding_model()
    assert model == mock_model_instance
    mock_sentence_transformer.assert_called_once_with(feedback_helper.EMBEDDING_MODEL)