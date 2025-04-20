import pytest
from unittest.mock import patch, MagicMock
from database.query_executor import execute_bigquery_query

@pytest.fixture
def mock_bigquery_client():
    with patch('database.query_executor.bigquery.Client') as mock_client:
        mock_job = MagicMock()
        mock_job.result.return_value = MagicMock()
        mock_client.return_value.query.return_value = mock_job
        yield mock_client

def test_execute_bigquery_query(mock_bigquery_client):
    test_query = "SELECT * FROM `test_dataset.test_table`"
    
    # Execute query
    execute_bigquery_query(test_query)
    
    # Verify BigQuery client was called correctly
    mock_bigquery_client.return_value.query.assert_called_once_with(test_query)