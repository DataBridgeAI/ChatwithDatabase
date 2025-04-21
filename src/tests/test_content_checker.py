import pytest
from query_checks.content_checker import sensitivity_filter

def test_sensitivity_filter():
    result = sensitivity_filter("Show me data about elderly customers")
    # The function returns a string message, not a boolean
    assert isinstance(result, str)
    assert "age-related" in result.lower()




