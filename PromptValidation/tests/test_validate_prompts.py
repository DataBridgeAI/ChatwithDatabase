import pytest
import json
from unittest.mock import Mock, patch
from PromptValidation.validate_prompts import validate_stored_prompts
from PromptValidation.prompt_validator import PromptValidator
from PromptValidation.config import EXPECTED_PROMPT_TEMPLATE

@patch('google.cloud.storage.Client')
def test_validate_stored_prompts(mock_storage):
    validator = PromptValidator("test-project", "test-bucket")

    # Create mock data that matches the expected template structure
    mock_data = {
        "version": EXPECTED_PROMPT_TEMPLATE["version"],
        "template": EXPECTED_PROMPT_TEMPLATE["template"],
        "metadata": EXPECTED_PROMPT_TEMPLATE["metadata"]
    }

    # Mock the blob and its properties
    mock_blob = Mock()
    mock_blob.name = "prompts/v1.json"
    mock_blob.download_as_string.return_value = bytes(json.dumps(mock_data), 'utf-8')

    # Mock the bucket
    mock_bucket = Mock()
    mock_bucket.list_blobs.return_value = [mock_blob]

    # Set up the storage client mock
    validator.storage_client.bucket.return_value = mock_bucket

    # Run the validation
    results = validate_stored_prompts(validator)

    # Verify the results
    assert isinstance(results, dict)
    assert "prompts/v1.json" in results
    assert not results["prompts/v1.json"]  # Should be empty list if valid

    # Verify the mock calls
    validator.storage_client.bucket.assert_called_once_with("test-bucket")
    mock_bucket.list_blobs.assert_called_once_with(prefix="prompts/")
    mock_blob.download_as_string.assert_called_once()

