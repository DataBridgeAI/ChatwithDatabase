# from google.cloud import bigquery
# import pandas as pd

# def execute_bigquery_query(query):
#     """Execute a SQL query on BigQuery and return results as a Pandas DataFrame."""
#     try:
#         client = bigquery.Client()
#         query_job = client.query(query)
#         result = query_job.result()
#         df = result.to_dataframe()

#         if df.empty:
#             return pd.DataFrame({"Message": ["No results found for the query."]})

#         return df

#     except Exception as e:
#         return pd.DataFrame({"Error": [str(e)], "SQL": [query]})
from google.cloud import bigquery
import pandas as pd
import os
import uuid
import dvc.api

DATA_DIR = "data/"  # Folder to store query results

def execute_bigquery_query(query):
    """Execute a SQL query on BigQuery and return results as a Pandas DataFrame."""
    try:
        client = bigquery.Client()
        query_job = client.query(query)
        result = query_job.result()
        df = result.to_dataframe()

        if df.empty:
            return pd.DataFrame({"Message": ["No results found for the query."]})

        # Save results with a unique identifier
        os.makedirs(DATA_DIR, exist_ok=True)
        query_id = str(uuid.uuid4())[:8]  # Generate short unique ID
        filename = f"{DATA_DIR}query_results_{query_id}.csv"
        df.to_csv(filename, index=False)

        # Track results with DVC
        os.system(f"dvc add {filename}")
        os.system(f"git add {filename}.dvc")
        os.system(f"git commit -m 'Add query result {query_id}'")

        return df

    except Exception as e:
        return pd.DataFrame({"Error": [str(e)], "SQL": [query]})
