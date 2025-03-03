import pytest
import pandas as pd
import tarfile
import os
from unittest.mock import patch, MagicMock
from google.cloud import bigquery
import chromadb
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

# Constants
test_csv_path = "/tmp/test_feedback_data.csv"
test_processed_csv_path = "/tmp/processed_feedback.csv"
test_chromadb_path = "/tmp/test_chroma_db"
test_chromadb_archive_path = "/tmp/chroma_db.tar.gz"

def test_extract_feedback_from_bigquery():
    mock_client = MagicMock()
    mock_query_job = MagicMock()
    mock_df = pd.DataFrame({
        "user_question": ["What is AI?"],
        "generated_sql": ["SELECT * FROM ai_data"],
        "corrected_sql": ["SELECT * FROM ai_data WHERE type='AI'"]
    })
    
    mock_query_job.to_dataframe.return_value = mock_df
    mock_client.query.return_value = mock_query_job
    
    with patch("google.cloud.bigquery.Client", return_value=mock_client):
        with patch("pandas.DataFrame.to_csv") as mock_to_csv:
            from feedback_processing import extract_feedback_from_bigquery
            extract_feedback_from_bigquery()
            mock_to_csv.assert_called()

def test_generate_embeddings():
    df = pd.DataFrame({"user_question": ["What is AI?"]})
    
    mock_embedding_model = MagicMock()
    mock_embedding_model.encode.return_value = [0.1, 0.2, 0.3]
    
    mock_chroma_client = MagicMock()
    mock_collection = MagicMock()
    mock_chroma_client.get_or_create_collection.return_value = mock_collection
    
    with patch("sentence_transformers.SentenceTransformer", return_value=mock_embedding_model):
        with patch("chromadb.PersistentClient", return_value=mock_chroma_client):
            with patch("pandas.DataFrame.to_csv") as mock_to_csv:
                from feedback_processing import generate_embeddings
                generate_embeddings()
                mock_to_csv.assert_called_with(test_processed_csv_path, index=False)

def test_archive_and_upload_chromadb():
    os.makedirs(test_chromadb_path, exist_ok=True)
    test_file = os.path.join(test_chromadb_path, "test.txt")
    with open(test_file, "w") as f:
        f.write("Test ChromaDB content")

    with patch("tarfile.open", MagicMock()) as mock_tar:
        from feedback_processing import archive_and_upload_chromadb
        archive_and_upload_chromadb()
        mock_tar.assert_called_with(test_chromadb_archive_path, "w:gz")
