from google.cloud import bigquery
import pandas as pd
import time

def execute_bigquery_query(query):
    """Execute a SQL query on BigQuery and return results as a Pandas DataFrame."""
    try:
        client = bigquery.Client()
        start_time = time.time()
        query_job = client.query(query)
        result = query_job.result()  # Waits for the query to finish
        execution_time = time.time() - start_time
        
        df = result.to_dataframe()
        
        if df.empty:
            return pd.DataFrame({"Message": ["No results found for the query."]}), execution_time

        return df, execution_time
    except Exception as error:
        return pd.DataFrame({"Error": [str(error)], "SQL": [query]}), 0
