from dotenv import load_dotenv
load_dotenv()  # Load all the environment variables

import streamlit as st
import os
import google.generativeai as genai
from google.cloud import bigquery

# Set up BigQuery client
def get_bigquery_client():
    return bigquery.Client.from_service_account_json("databridgeai-db5fd1b46c4c.json")

# Function to extract the schema of the BigQuery table
def get_table_schema():
    client = get_bigquery_client()
    table_ref = client.dataset('llmops_dataset').table('sample_table')  # Change dataset and table name if needed
    table = client.get_table(table_ref)  # Fetch the table
    schema = table.schema  # Extract schema
    return schema

# Function to execute SQL query on BigQuery
def read_sql_query(sql):
    client = get_bigquery_client()
    try:
        print(f"Executing SQL: {sql}")  # Debugging: print the exact query

        query_job = client.query(sql)
        results = query_job.result()  # Force execution
        
        if query_job.error_result:
            print(f"Query failed with error: {query_job.error_result}")
            return None
        
        return results
    except Exception as e:
        print(f"Query execution failed: {e}")
        return None


# Function to convert schema into column names
def get_column_names_from_schema(schema):
    column_names = [field.name for field in schema]
    print(f"Extracted Column Names: {column_names}")  # Debugging
    return column_names


# Configure Genai Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Google Gemini Model and provide queries as response
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], question])
    return response.text.strip()  # Ensure clean SQL output

## Define Your Prompt
prompt = [
    """
    You are an expert in converting English questions to SQL queries!
    The SQL database is in Google BigQuery and has the following table:

    Dataset Name: databridgeai.llmops_dataset
    Table Name: sample_table
    Columns: [UNKNOWN] (This will be dynamically fetched)

    Example 1 - How many student records are present?  
    SQL: SELECT COUNT(*) FROM `databridgeai.llmops_dataset.sample_table`;

    Example 2 - Show all students studying Data Science.  
    SQL: SELECT * FROM `databridgeai.llmops_dataset.sample_table` WHERE CLASS='Data Science';

    Your output should only contain the SQL query with no explanations.
    """
]

# Streamlit App Setup
st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("Gemini App To Retrieve SQL Data")

# User input for the question
question = st.text_input("Input: ", key="input")
submit = st.button("Ask the question")

# If submit is clicked
if submit:
    # Step 1: Fetch the schema from BigQuery
    schema = get_table_schema()  # Extract schema from the table
    column_names = get_column_names_from_schema(schema)  # Get column names

    # Step 2: Dynamically update the prompt to include columns
    prompt[0] = prompt[0].replace("[UNKNOWN]", ", ".join(column_names))  # Update prompt with actual columns
    
    # Step 3: Generate the SQL query based on the user input
   # Ensure the query does not contain unnecessary formatting
    response = get_gemini_response(question, prompt)
    cleaned_query = response.strip().strip("```sql").strip("```")  # Remove markdown artifacts
    print(f"Executing SQL Query: {cleaned_query}")
    query_result = read_sql_query(cleaned_query)
    
    # Step 5: Display the result in Streamlit
    if query_result:
        st.subheader("The Response is:")
        for row in query_result:
            # Dynamically create a dictionary from the row (based on column names)
            row_dict = dict(zip(column_names, row))
            st.write(row_dict)  # Display the row as a dictionary (column names as keys)
    else:
        st.error("Query execution failed.")
