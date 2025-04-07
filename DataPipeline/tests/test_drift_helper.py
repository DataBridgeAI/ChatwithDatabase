import pytest
from unittest import mock
import json
import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

# Mock airflow before importing drift_helper
sys.modules["airflow"] = MagicMock()
sys.modules["airflow.providers"] = MagicMock()
sys.modules["airflow.providers.slack"] = MagicMock()
sys.modules["airflow.providers.slack.operators"] = MagicMock()
sys.modules["airflow.providers.slack.operators.slack_webhook"] = MagicMock()

from drift_helper import check_schema_drift, check_data_drift, send_slack_alert

@pytest.fixture
def mock_bigquery_client():
    with mock.patch("drift_helper.bigquery.Client") as mock_client:
        yield mock_client

@pytest.fixture
def mock_storage_client():
    with mock.patch("drift_helper.storage.Client") as mock_client:
        yield mock_client

@pytest.fixture
def mock_xcom():
    return mock.MagicMock()

@pytest.fixture
def mock_slack_operator():
    with mock.patch("drift_helper.SlackWebhookOperator") as mock_slack:
        yield mock_slack

def test_check_schema_drift(mock_bigquery_client, mock_storage_client, mock_xcom):
    mock_bq = mock_bigquery_client.return_value
    mock_storage = mock_storage_client.return_value

    # Mock BigQuery schema with proper strings
    mock_bq.list_tables.return_value = [mock.Mock(table_id="test_table")]
    mock_bq.get_table.return_value.schema = [
        mock.Mock(name="col1", field_type="STRING")  # Correctly mock attributes
    ]
    for field in mock_bq.get_table.return_value.schema:
        field.name = "col1"  # Make sure to use valid strings
        field.field_type = "STRING"

    # Mock GCS schema
    mock_bucket = mock_storage.bucket.return_value
    mock_blob = mock_bucket.blob.return_value
    mock_blob.exists.return_value = True
    mock_blob.download_as_text.return_value = json.dumps({"test_table": {"col1": "STRING"}})

    kwargs = {"ti": mock_xcom}

    # Run the check_schema_drift function
    check_schema_drift(**kwargs)

def test_check_data_drift(mock_bigquery_client, mock_storage_client, mock_xcom):
    mock_bq = mock_bigquery_client.return_value
    mock_storage = mock_storage_client.return_value
    
    # Mock BigQuery table
    mock_bq.list_tables.return_value = [mock.Mock(table_id="test_table")]
    
    # Mock dataframe methods (fix)
    mock_bq.query.return_value.to_dataframe.return_value.mean.return_value.to_dict.return_value = {"col1": 3.0, "col2": 25.0}
    mock_bq.query.return_value.to_dataframe.return_value.std.return_value.to_dict.return_value = {"col1": 1.5, "col2": 15.0}
    mock_bq.query.return_value.to_dataframe.return_value.isnull.return_value.mean.return_value.to_dict.return_value = {"col1": 0.0, "col2": 0.0}
    
    # Mock GCS statistics
    mock_bucket = mock_storage.bucket.return_value
    mock_blob = mock_bucket.blob.return_value
    mock_blob.exists.return_value = True
    mock_blob.download_as_text.return_value = json.dumps({
        "test_table": {
            "mean": {"col1": 3.0, "col2": 25.0},
            "std": {"col1": 1.5, "col2": 15.0},
            "null_percent": {"col1": 0.0, "col2": 0.0},
        }
    })
    
    kwargs = {"ti": mock_xcom}
    check_data_drift(**kwargs)
    mock_xcom.xcom_push.assert_not_called()  # No drift should be detected

def test_send_slack_alert(mock_xcom, mock_slack_operator):
    mock_xcom.xcom_pull.side_effect = [None, "⚠️ Data Drift Detected"]  # Simulate drift detection
    kwargs = {"ti": mock_xcom, "dag": mock.Mock()}
    send_slack_alert(**kwargs)
    mock_slack_operator.assert_called_once()
