# import streamlit as st
# import pandas as pd
# from database.query_executor import execute_bigquery_query
# from database.schema import get_bigquery_schema

# from ai.llm import generate_sql
# from ui.layout import render_sidebar
# from ui.visualization import visualize_data
 
 
# st.set_page_config(page_title="BigQuery Analytics", layout="wide", page_icon="📊")

# # Initialize session state
# if 'schema' not in st.session_state:
#     st.session_state.schema = None
# if 'result' not in st.session_state:
#     st.session_state.result = None
# if 'generated_sql' not in st.session_state:
#     st.session_state.generated_sql = ""

# # Render sidebar & fetch project ID and dataset
# project_id, dataset_id = render_sidebar()

# # Display Schema (Only for the User-Specified Dataset)
# if st.session_state.schema:
#     st.divider()
#     st.markdown(st.session_state.schema)

# st.title("📊 BigQuery Analytics Dashboard")

# user_query = st.text_area(
#     "Enter your question:", 
#     "Show top 10 artists based on popularity",
#     height=100
# )

# if st.button("🚀 Generate & Execute Query"):
#     if not st.session_state.schema:
#         st.error("Please load the BigQuery schema first!")
#     else:
#         with st.spinner("Generating SQL query..."):
#             generated_sql = generate_sql(user_query, st.session_state.schema, project_id, dataset_id)
#             st.session_state.generated_sql = generated_sql
            
#         with st.spinner("Executing SQL query..."):
#             result = execute_bigquery_query(generated_sql)

#             if result.empty or "Error" in result.columns:
#                 st.session_state.result = None
#                 st.error("❌ No data returned or an error occurred.")
#                 if "Error" in result.columns:
#                     st.error(result["Error"][0])
#                 with st.expander("🔎 View Generated SQL", expanded=False):
#                     st.code(st.session_state.generated_sql, language='sql')
#             else:
#                 st.session_state.result = result

# # Display Results
# if st.session_state.result is not None:
#     st.divider()
#     st.subheader("🔍 Query Results")
#     st.dataframe(st.session_state.result, use_container_width=True)

#     with st.expander("🔎 View Generated SQL", expanded=False):
#         st.code(st.session_state.generated_sql, language='sql')

#     # Trigger Visualization
#     visualize_data(st.session_state.result)
import streamlit as st
import pandas as pd
from database.query_executor import execute_bigquery_query
from ai.llm import generate_sql
from ui.layout import render_sidebar
from ui.visualization import visualize_data

st.set_page_config(page_title="BigQuery Analytics", layout="wide", page_icon="📊")

# ✅ Ensure all session state variables are initialized before use
if "schema" not in st.session_state:
    st.session_state.schema = None
if "result" not in st.session_state:
    st.session_state.result = None  # ✅ Fix: Initialize to None
if "generated_sql" not in st.session_state:
    st.session_state.generated_sql = ""

# Render sidebar & fetch project ID and dataset
project_id, dataset_id = render_sidebar()

# Display Schema
if st.session_state.schema:
    st.divider()
    st.markdown(st.session_state.schema)

st.title("📊 BigQuery Analytics Dashboard")

user_query = st.text_area(
    "Enter your question:", 
    "Show total sales for each product category",
    height=100
)

if st.button("🚀 Generate & Execute Query"):
    if not st.session_state.schema:
        st.error("Please load the BigQuery schema first!")
    else:
        with st.spinner("Generating SQL query..."):
            generated_sql = generate_sql(user_query, st.session_state.schema, project_id, dataset_id)
            st.session_state.generated_sql = generated_sql
            
        with st.spinner("Executing SQL query..."):
            result = execute_bigquery_query(generated_sql)

            if result.empty or "Error" in result.columns:
                st.session_state.result = None  # ✅ Fix: Set to None if no data
                st.error("❌ No data returned or an error occurred.")
                if "Error" in result.columns:
                    st.error(result["Error"][0])
                with st.expander("🔎 View Generated SQL", expanded=False):
                    st.code(st.session_state.generated_sql, language='sql')
            else:
                st.session_state.result = result

# ✅ Ensure `st.session_state.result` is initialized before use
if "result" in st.session_state and st.session_state.result is not None:
    st.divider()
    st.subheader("🔍 Query Results")
    st.dataframe(st.session_state.result, use_container_width=True)

    with st.expander("🔎 View Generated SQL", expanded=False):
        st.code(st.session_state.generated_sql, language='sql')

    # Trigger Visualization
    visualize_data(st.session_state.result)
