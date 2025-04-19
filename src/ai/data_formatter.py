import json
import pandas as pd
from typing import Dict, Any
from datetime import datetime, date
from google.cloud.bigquery import Row

def dataframe_to_json(df: pd.DataFrame, max_size_mb: int = 10) -> Dict[str, Any]:
    """Convert DataFrame to JSON with size check and timestamp handling"""
    try:
        # Create a copy to avoid modifying the original DataFrame
        df = df.copy()
        
        # Handle all timestamp-like columns
        for col in df.columns:
            # Check if column contains datetime-like data
            if (df[col].dtype.name in ['datetime64[ns]', 'datetime64', 'timestamp'] or
                str(df[col].dtype).startswith('datetime') or
                (not df.empty and isinstance(df[col].iloc[0], (datetime, date)))):
                df[col] = df[col].apply(lambda x: x.isoformat() if pd.notnull(x) else None)
        
        # Convert DataFrame to JSON records
        json_data = df.to_dict(orient='records')
        
        # Additional JSON serialization check with enhanced datetime handling
        def json_serial(obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            if isinstance(obj, Row):
                return dict(obj)
            raise TypeError(f"Type {type(obj)} not serializable")
        
        # Verify JSON serialization
        json_str = json.dumps(json_data, default=json_serial)
        size_mb = len(json_str.encode('utf-8')) / (1024 * 1024)
        
        if size_mb > max_size_mb:
            raise ValueError(f"Result size ({size_mb:.1f}MB) exceeds limit of {max_size_mb}MB")
            
        return json.loads(json_str)  # Return the validated JSON-compatible dictionary
    except Exception as e:
        print(f"Error in dataframe_to_json: {str(e)}")
        raise Exception(f"Failed to convert data to JSON: {str(e)}")
