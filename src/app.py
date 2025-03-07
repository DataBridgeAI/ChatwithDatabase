import streamlit as st
import pandas as pd

from database.query_executor import execute_bigquery_query
from database.schema import get_bigquery_schema
from ai.llm import generate_sql
from ui.layout import render_sidebar
from ui.visualization import visualize_data
from ai.query_validator import validate_query  # Assuming query_validator is defined in a separate file


st.set_page_config(
    page_title="BigQuery Analytics",
    layout="wide",
    page_icon="📊"
)

# Initialize session state
if "schema" not in st.session_state:
    st.session_state.schema = None
if "result" not in st.session_state:
    st.session_state.result = None
if "generated_sql" not in st.session_state:
    st.session_state.generated_sql = ""

# Render sidebar & fetch project ID and dataset
project_id, dataset_id = render_sidebar()

st.title("📊 BigQuery Analytics Dashboard")

# Display Schema
if st.session_state.schema:
    st.divider()
    with st.expander("Schema Overview", expanded=False):
        st.markdown(st.session_state.schema)

user_query = st.text_area(
    "Enter your question:",
    "Show top 10 artists based on popularity",
    height=100
)

if st.button("Generate & Execute Query"):
    if not st.session_state.schema:
        st.error("Please load the BigQuery schema first!")
    else:
        # Validate the user query before generating SQL
        validation_error = validate_query(user_query)
        
        if validation_error:
            # If the query is invalid, show the error and don't proceed further
            st.error(validation_error)
        else:
            with st.spinner("Generating SQL query..."):
                generated_sql = generate_sql(
                    user_query, st.session_state.schema, project_id, dataset_id
                )
                st.session_state.generated_sql = generated_sql

            with st.spinner("Executing SQL query..."):
                result = execute_bigquery_query(generated_sql)

                if result.empty or "Error" in result.columns:
                    st.session_state.result = None
                    st.error("No data returned or an error occurred.")
                    
                    if "Error" in result.columns:
                        st.error(result["Error"][0])
                    
                    with st.expander("View Generated SQL", expanded=False):
                        st.code(st.session_state.generated_sql, language="sql")
                else:
                    st.session_state.result = result

# Display Results
if st.session_state.result is not None:
    st.divider()
    st.subheader("🔍 Query Results")
    st.dataframe(st.session_state.result, use_container_width=True)

    with st.expander("View Generated SQL", expanded=False):
        st.code(st.session_state.generated_sql, language="sql")

    # Trigger Visualization
    visualize_data(st.session_state.result)
