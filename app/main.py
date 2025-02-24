import streamlit as st
import redis
import json
import requests
from airflow.api.client import Client

# Connect to Redis
redis_client = redis.Redis(host='redis', port=6379, db=0)

# Function to trigger the Airflow DAG to process the user query
def trigger_dag(user_query):
    client = Client(None, None)  # No need to provide any arguments
    client.trigger_dag(dag_id='query_processing_dag', conf={'user_query': user_query})

# Function to retrieve the schema from Redis
def get_schema_from_redis():
    schema_data = redis_client.get('latest_schema')
    if schema_data:
        return json.loads(schema_data)
    else:
        return None

# Function to send the schema to LLM (dummy function to simulate LLM interaction)
def llm_generate_query(prompt):
    # Simulate the LLM response (You should integrate with your actual LLM here)
    return f"Generated SQL query for: {prompt}"

# Main Streamlit app
def main():
    st.title('Text-to-SQL Chatbot')

    # Get the user query
    user_query = st.text_input("Ask a question:")

    if user_query:
        # Trigger the Airflow DAG when the user submits the query
        trigger_dag(user_query)
        st.write("DAG triggered for processing the query...")

        # Poll Redis to check if the schema is available after DAG processing
        relevant_schema = get_schema_from_redis()

        if relevant_schema:
            st.write("Relevant Schema:", relevant_schema)

            # Use the schema in LLM to generate the SQL query (or other relevant responses)
            llm_prompt = f"Using this schema: {relevant_schema}, answer the following query: {user_query}"
            llm_response = llm_generate_query(llm_prompt)
            st.write("LLM Response: ", llm_response)
        else:
            st.write("No relevant schema found. Please try again later.")

if __name__ == "__main__":
    main()
