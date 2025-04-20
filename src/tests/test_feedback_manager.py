import pytest
from unittest.mock import patch, MagicMock
from feedback.feedback_manager import store_feedback

@pytest.fixture
def mock_bigquery():
    with patch('google.cloud.bigquery.Client') as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client

def test_store_feedback(mock_bigquery):
    store_feedback("test query", "SELECT *", "👍 Yes")
    mock_bigquery.insert_rows_json.assert_called_once()

def test_store_feedback_negative(mock_bigquery):
    store_feedback("test query", "SELECT *", "👎 No")
    mock_bigquery.insert_rows_json.assert_called_once()

def test_store_feedback_invalid(mock_bigquery):
    store_feedback("test query", "SELECT *", "invalid")
    mock_bigquery.insert_rows_json.assert_called_once()


