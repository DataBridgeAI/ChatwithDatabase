from google.cloud import bigquery
import streamlit as st

def get_bigquery_schema(project_id, dataset_id):
    """Fetch schema details for the specified dataset in BigQuery."""
    try:
        client = bigquery.Client(project=project_id)
        dataset_ref = client.dataset(dataset_id, project=project_id)
        tables = list(client.list_tables(dataset_ref))

        if not tables:
            return f"⚠ No tables found in dataset `{dataset_id}`."

        schema_info = f"📚 **BigQuery Schema for `{dataset_id}`**\n"

        for table in tables:
            table_id = table.table_id
            schema_info += f"\n### Table: `{table_id}`\n"

            # Fetch table schema
            table_ref = client.get_table(f"{project_id}.{dataset_id}.{table_id}")
            schema_info += "**Columns:**\n"

            for field in table_ref.schema:
                schema_info += f"- `{field.name}` ({field.field_type})\n"

        return schema_info

    except Exception as e:
        st.error(f"Schema retrieval error: {e}")
        return None
