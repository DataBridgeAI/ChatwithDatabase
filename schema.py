# from google.cloud import bigquery

# def get_bigquery_schema():
#     client = bigquery.Client()
#     dataset_ref = client.dataset("llmops_dataset")
#     dataset = client.get_dataset(dataset_ref)
#     schema_info = {}

#     for table in dataset.tables:
#         table_ref = client.get_table(table)
#         schema_info[table.table_id] = [field.name for field in table_ref.schema]

#     return schema_info
from google.cloud import bigquery

def get_bigquery_schema():
    client = bigquery.Client()
    
    dataset_id = "llmops_dataset"  # ❗ Update this with your actual project ID and dataset name
    dataset_ref = client.dataset(dataset_id)
    
    tables = client.list_tables(dataset_ref)

    schema_info = {}
    for table in tables:
        table_ref = dataset_ref.table(table.table_id)
        table_schema = client.get_table(table_ref).schema

        schema_info[table.table_id] = [
            {"name": field.name, "type": field.field_type} for field in table_schema
        ]

    return schema_info
