import pytest
from unittest.mock import patch, MagicMock, call
from PromptValidation.bias_check import check_bias_in_queries
from PromptValidation.prompt_validator import PromptValidator
from PromptValidation.test_queries import TEST_QUERIES
from PromptValidation.config import (
    PROJECT_ID, 
    PROMPT_BUCKET_NAME, 
    RETAIL_SCHEMA, 
    DATASET_ID
)

@pytest.fixture
def mock_generate_sql():
    with patch('PromptValidation.bias_check.generate_sql') as mock:  # Updated import path
        mock.return_value = """
        SELECT * FROM `chatwithdata-451800.RetailDataset.customers`
        WHERE gender = 'female'
        """
        yield mock

@pytest.fixture
def mock_prompt_template():
    with patch('src.ai.llm.load_prompt_template') as mock:  # Updated import path
        yield mock

@pytest.fixture
def validator():
    return PromptValidator(PROJECT_ID, PROMPT_BUCKET_NAME)

def test_check_bias_in_queries(mock_generate_sql, mock_prompt_template, validator):
    # Test with queries that should trigger bias detection
    test_queries = [
        "Show sales data filtered by customer gender",
        "Compare spending between male and female customers"
    ]
    
    # Mock the validator's check_for_bias method to ensure it returns expected results
    with patch.object(validator, 'check_for_bias') as mock_check_bias:
        mock_check_bias.return_value = {
            'gender_bias': True,
            'racial_bias': False,
            'age_bias': False
        }
        
        results = check_bias_in_queries(test_queries, validator)
    
    assert isinstance(results, dict)
    assert all(key in results for key in ['gender_bias', 'racial_bias', 'age_bias'])
    assert len(results['gender_bias']) > 0
    assert test_queries[0] in results['gender_bias']
    
    # Verify generate_sql was called for both queries
    assert mock_generate_sql.call_count == 2
    
    # Verify the calls to generate_sql
    mock_generate_sql.assert_has_calls([
        call(
            user_query=test_queries[0],
            schema=RETAIL_SCHEMA,
            project_id=PROJECT_ID,
            dataset_id=DATASET_ID
        ),
        call(
            user_query=test_queries[1],
            schema=RETAIL_SCHEMA,
            project_id=PROJECT_ID,
            dataset_id=DATASET_ID
        )
    ], any_order=True)






