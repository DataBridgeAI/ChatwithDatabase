import pytest
from PromptValidation.prompt_monitor import PromptMonitor
from PromptValidation.prompt_validator import PromptValidator

@pytest.fixture
def monitor():
    validator = PromptValidator("test-project", "test-bucket")
    return PromptMonitor(validator)

def test_should_update_prompt(monitor):
    # Should update when bias detected
    bias_results = {
        'gender_bias': True,
        'racial_bias': False,
        'age_bias': False
    }
    validation_results = {'sql_validation': 'passed'}
    assert monitor.should_update_prompt(bias_results, validation_results)
    
    # Should update when validation fails
    bias_results = {
        'gender_bias': False,
        'racial_bias': False,
        'age_bias': False
    }
    validation_results = {'sql_validation': 'failed'}
    assert monitor.should_update_prompt(bias_results, validation_results)
    
    # Should not update when everything passes
    bias_results = {
        'gender_bias': False,
        'racial_bias': False,
        'age_bias': False
    }
    validation_results = {'sql_validation': 'passed'}
    assert not monitor.should_update_prompt(bias_results, validation_results)
