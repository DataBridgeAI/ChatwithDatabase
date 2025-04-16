import json
import pandas as pd
from typing import Dict, Any

def dataframe_to_json(df: pd.DataFrame, max_size_mb: int = 10) -> Dict[str, Any]:
    """Convert DataFrame to JSON with size check"""
    try:
        # Convert DataFrame to JSON records
        json_data = df.to_dict(orient='records')
        
        # Check size (approximate)
        json_str = json.dumps(json_data)
        size_mb = len(json_str.encode('utf-8')) / (1024 * 1024)
        
        if size_mb > max_size_mb:
            raise ValueError(f"Result size ({size_mb:.1f}MB) exceeds limit of {max_size_mb}MB")
            
        return json_data
    except Exception as e:
        print(f"Error in dataframe_to_json: {str(e)}")  # Add logging
        raise Exception(f"Failed to convert data to JSON: {str(e)}")
