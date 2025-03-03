from google.cloud import bigquery
import pandas as pd

def execute_bigquery_query(query):
    """Execute a SQL query on BigQuery and return results as a Pandas DataFrame."""
    try:
        client = bigquery.Client()
        query_job = client.query(query)
        result = query_job.result()
        df = result.to_dataframe()

        if df.empty:
            return pd.DataFrame({"Message": ["No results found for the query."]})

        return df
    except Exception as error:
        return pd.DataFrame({"Error": [str(error)], "SQL": [query]})
