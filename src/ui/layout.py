import os
import streamlit as st
from database.schema import get_bigquery_schema

def render_sidebar():
    """Render sidebar for BigQuery configuration and schema loading."""
    with st.sidebar.expander("BigQuery Configuration", expanded=True):
        project_id = st.text_input("Project ID", "your-gcp-project-id")
        dataset_id = st.text_input("Dataset ID", "your-dataset")

        if st.button("📥 Load Schema", use_container_width=True):
            with st.spinner(f"Fetching schema for `{dataset_id}`..."):
                schema = get_bigquery_schema(project_id, dataset_id)
                if schema:
                    st.session_state.schema = schema
                    st.success(f"Schema for `{dataset_id}` loaded successfully!")

    return project_id, dataset_id
