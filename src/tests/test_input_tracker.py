import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import monitoring.input_tracker as it

@pytest.fixture
def tracker():
    return it.InputTracker()

@patch("monitoring.input_tracker.InputTracker._send_alert")
def test_track_invalid_input_calls_alert(mock_send_alert, tracker):
    tracker.track_invalid_input("bad query", "bias_error", {"field": "name"})
    
    assert len(tracker.invalid_inputs) == 1
    invalid_input = tracker.invalid_inputs[0]
    
    assert invalid_input.query == "bad query"
    assert invalid_input.error_type == "bias_error"
    assert isinstance(invalid_input.timestamp, datetime)
    assert invalid_input.validation_details == {"field": "name"}
    mock_send_alert.assert_called_once()

def test_analyze_root_cause_bias(tracker):
    result = tracker._analyze_root_cause("bias issue", ["query1"])
    assert result["category"] == "Bias Detection"

def test_analyze_root_cause_relevance(tracker):
    result = tracker._analyze_root_cause("relevance issue", ["query2"])
    assert result["category"] == "Schema Relevance"

def test_analyze_root_cause_sql_injection(tracker):
    result = tracker._analyze_root_cause("sql_injection attempt", ["query3"])
    assert result["category"] == "Security"

def test_analyze_root_cause_general(tracker):
    result = tracker._analyze_root_cause("unknown_error", ["query4"])
    assert result["category"] == "General Validation"

def test_get_recommended_actions_bias(tracker):
    actions = tracker._get_recommended_actions("bias")
    assert any("bias detection" in action.lower() for action in actions)

def test_get_recommended_actions_relevance(tracker):
    actions = tracker._get_recommended_actions("relevance")
    assert any("schema" in action.lower() for action in actions)

def test_get_recommended_actions_sql_injection(tracker):
    actions = tracker._get_recommended_actions("sql_injection")
    assert any("security" in action.lower() for action in actions)

def test_get_recommended_actions_general(tracker):
    actions = tracker._get_recommended_actions("unknown")
    assert "Review and update input validation rules" in actions

def test_format_slack_message_structure(tracker):
    alert = {
        "alert_type": "Invalid Input Detected",
        "timestamp": datetime.now().isoformat(),
        "details": {
            "query": "test",
            "error_type": "bias",
            "validation_details": {"foo": "bar"}
        },
        "root_cause_analysis": {
            "category": "Bias Detection",
            "likely_cause": "Cause",
            "pattern_detected": "Pattern"
        },
        "recommended_actions": ["Action 1", "Action 2"]
    }

    msg = tracker._format_slack_message(alert)
    assert "🚨 *Invalid Input Detected*" in msg
    assert "*Query Details:*" in msg
    assert "*Root Cause Analysis:*" in msg
    assert "*Recommended Actions:*" in msg

@patch("monitoring.input_tracker.requests.post")
@patch("monitoring.input_tracker.logger")
def test_send_alert_success(mock_logger, mock_post, tracker):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    alert = {
        "alert_type": "Invalid Input Detected",
        "timestamp": datetime.now().isoformat(),
        "details": {
            "query": "test",
            "error_type": "bias",
            "validation_details": {"foo": "bar"}
        },
        "root_cause_analysis": {
            "category": "Bias Detection",
            "likely_cause": "Cause",
            "pattern_detected": "Pattern"
        },
        "recommended_actions": ["Action 1", "Action 2"]
    }

    tracker._send_alert(alert)
    mock_post.assert_called_once()
    mock_logger.info.assert_called_with("Slack alert sent successfully")

@patch("monitoring.input_tracker.requests.post")
@patch("monitoring.input_tracker.logger")
def test_send_alert_failure(mock_logger, mock_post, tracker):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "error"
    mock_post.return_value = mock_response

    alert = {
        "alert_type": "Invalid Input Detected",
        "timestamp": datetime.now().isoformat(),
        "details": {
            "query": "test",
            "error_type": "bias",
            "validation_details": {"foo": "bar"}
        },
        "root_cause_analysis": {
            "category": "Bias Detection",
            "likely_cause": "Cause",
            "pattern_detected": "Pattern"
        },
        "recommended_actions": ["Action 1", "Action 2"]
    }

    tracker._send_alert(alert)
    mock_logger.error.assert_called_with("Failed to send Slack alert. Status: 400, Response: error")
