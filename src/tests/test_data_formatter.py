import pytest
import pandas as pd
from ai.data_formatter import dataframe_to_json

def test_dataframe_to_json():
    # Create a test DataFrame
    df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
    result = dataframe_to_json(df)
    # Update assertion to check for list instead of str
    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(item, dict) for item in result)


