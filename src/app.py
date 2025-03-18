
import streamlit as st
import pandas as pd
import time

from database.query_executor import execute_bigquery_query
from database.schema import get_bigquery_schema
from ai.llm import generate_sql
from ui.layout import render_sidebar
from ui.visualization import visualize_data
from ai.query_validator import validate_query
from feedback.feedback_manager import store_feedback
from feedback.vector_search import retrieve_similar_query
from feedback.chroma_setup import download_and_extract_chromadb
from monitoring.mlflow_config import setup_mlflow, log_query_generation

# Setup ChromaDB at startup
try:
    download_and_extract_chromadb()
except Exception as e:
    st.error(f"Failed to setup ChromaDB: {str(e)}")

# Initialize MLflow at startup - wrap in try-except to handle potential errors
try:
    experiment_id = setup_mlflow()
    print(f"MLflow initialized with experiment ID: {experiment_id}")
except Exception as e:
    print(f"Error initializing MLflow: {str(e)}")

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
if "user_query" not in st.session_state:
    st.session_state.user_query = "Show top 10 artists based on popularity"
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False
if "use_suggested" not in st.session_state:
    st.session_state.use_suggested = "Select an option"
if "viz_option" not in st.session_state:
    st.session_state.viz_option = "Select an option"
if "showing_suggestion" not in st.session_state:
    st.session_state.showing_suggestion = False
if "similar_query" not in st.session_state:
    st.session_state.similar_query = None
if "past_sql" not in st.session_state:
    st.session_state.past_sql = None
if "waiting_for_choice" not in st.session_state:
    st.session_state.waiting_for_choice = False


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
    st.session_state.user_query,
    height=100,
    key="query_input"
)


def reset_states():
    """Reset all relevant session states when generating new query"""
    st.session_state.result = None
    st.session_state.generated_sql = ""
    st.session_state.feedback_submitted = False
    st.session_state.user_query = user_query
    st.session_state.use_suggested = "Select an option"
    st.session_state.viz_option = "Select an option"
    st.session_state.showing_suggestion = False
    st.session_state.similar_query = None
    st.session_state.past_sql = None
    st.session_state.waiting_for_choice = False
    # Ensure the radio buttons are reset
    if "use_suggested" in st.session_state:
        del st.session_state.use_suggested
    if "viz_option" in st.session_state:
        del st.session_state.viz_option

def execute_new_query(start_time):
    """Execute new query generation with MLflow tracking"""
    error = None
    try:
        with st.spinner("Generating SQL query..."):
            st.session_state.generated_sql = generate_sql(
                st.session_state.user_query,
                st.session_state.schema,
                project_id,
                dataset_id
            )
        
        with st.spinner("Executing SQL query..."):
            result = execute_bigquery_query(st.session_state.generated_sql)
            if result.empty or "Error" in result.columns:
                st.session_state.result = None
                error = "No data returned or an error occurred."
                st.error(error)
                if "Error" in result.columns:
                    error = result["Error"][0]
                    st.error(error)
            else:
                st.session_state.result = result
    except Exception as e:
        error = str(e)
        st.error(f"Error: {error}")
    finally:
        try:
            # Log to MLflow
            log_query_generation(
                user_query=st.session_state.user_query,
                generated_sql=st.session_state.generated_sql,
                execution_time=time.time() - start_time,
                error=error,
                similar_query_found=False,
                metadata={
                    "dataset": dataset_id,
                    "project": project_id
                }
            )
        except Exception as e:
            print(f"Error logging to MLflow: {str(e)}")

if st.button("Generate & Execute Query"):
    reset_states()
    st.session_state.start_time = time.time()  # Store start_time in session state
    
    if not st.session_state.schema:
        st.error("Please load the BigQuery schema first!")
    else:
        # Validate query
        validation_error = validate_query(user_query)
        if validation_error:
            st.error(validation_error)
            log_query_generation(
                user_query=user_query,
                generated_sql="",
                execution_time=time.time() - st.session_state.start_time,
                error=validation_error
            )
            st.stop()
        
        # Try to find similar query
        similar_query, past_sql = retrieve_similar_query(user_query)
        
        if similar_query and past_sql:
            st.session_state.similar_query = similar_query
            st.session_state.past_sql = past_sql
            st.session_state.showing_suggestion = True
            st.session_state.waiting_for_choice = True
        else:
            execute_new_query(st.session_state.start_time)  # Use start_time from session state

if st.session_state.get('waiting_for_choice', False):
    st.write("Similar query found:", st.session_state.similar_query)
    st.write("Suggested SQL:", st.session_state.past_sql)
    
    use_suggested = st.radio(
        "Would you like to use the suggested SQL query instead of generating a new one?",
        ["Select an option", "Yes", "No"],
        key="use_suggested"
    )
    
    if use_suggested != "Select an option":
        st.session_state.waiting_for_choice = False  # Reset the flag
        
        if use_suggested == "Yes":
            st.session_state.generated_sql = st.session_state.past_sql
            # Execute the suggested query
            with st.spinner("Executing suggested SQL query..."):
                result = execute_bigquery_query(st.session_state.generated_sql)
                if result.empty or "Error" in result.columns:
                    st.session_state.result = None
                    st.error("No data returned or an error occurred.")
                    if "Error" in result.columns:
                        st.error(result["Error"][0])
                else:
                    st.session_state.result = result
        else:  # No
            execute_new_query(st.session_state.start_time)

# Display Results and Collect Feedback
if st.session_state.result is not None:
    st.divider()
    st.subheader("🔍 Query Results")
    st.dataframe(st.session_state.result, use_container_width=True)

    with st.expander("View Generated SQL", expanded=False):
        st.code(st.session_state.generated_sql, language="sql")

    # Feedback Section
    if not st.session_state.feedback_submitted:
        st.write("Was this SQL query helpful?")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👍 Yes"):
                store_feedback(user_query, st.session_state.generated_sql, "👍 Yes")
                log_query_generation(
                    user_query=user_query,
                    generated_sql=st.session_state.generated_sql,
                    execution_time=time.time() - st.session_state.get('start_time', time.time()),
                    feedback="👍 Yes",
                    similar_query_found=bool(st.session_state.get('similar_query'))
                )
                st.session_state.feedback_submitted = True
                st.success("Thank you for your feedback!")
                
        with col2:
            if st.button("👎 No"):
                store_feedback(user_query, st.session_state.generated_sql, "👎 No")
                log_query_generation(
                    user_query=user_query,
                    generated_sql=st.session_state.generated_sql,
                    execution_time=time.time() - st.session_state.get('start_time', time.time()),
                    feedback="👎 No",
                    similar_query_found=bool(st.session_state.get('similar_query'))
                )
                st.session_state.feedback_submitted = True
                st.success("Thank you for your feedback!")

    # Visualization Option
    show_viz = st.radio(
        "Would you like to see visualizations?", 
        ["Select an option", "Yes", "No"],
        key="viz_option"
    )
    if show_viz == "Select an option":
        st.warning("Please select whether you want to see visualizations or not")
        st.stop()
    elif show_viz == "Yes":
        visualize_data(st.session_state.result)
