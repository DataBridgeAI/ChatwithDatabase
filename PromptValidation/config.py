"""Configuration settings for model validation"""
import json
from google.cloud import storage

# GCP Configuration
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
PROMPT_BUCKET_NAME = "sql-prompts-store"

RETAIL_SCHEMA = {
    "Customers": {
        "CustomerID": "INTEGER",
        "FirstName": "STRING",
        "LastName": "STRING",
        "Email": "STRING",
        "Address": "STRING",
        "City": "STRING",
        "State": "STRING",
        "ZipCode": "STRING",
        "RegistrationDate": "DATE"
    },
    "OrderItems": {
        "OrderItemID": "INTEGER",
        "OrderID": "INTEGER",
        "ProductID": "INTEGER",
        "Quantity": "INTEGER",
        "UnitPrice": "FLOAT"
    },
    "Orders": {
        "OrderID": "INTEGER",
        "CustomerID": "INTEGER",
        "OrderDate": "TIMESTAMP",
        "OrderStatus": "STRING",
        "ShippingAddress": "STRING",
        "TotalAmount": "FLOAT"
    },
    "ProductReviews": {
        "ReviewID": "INTEGER",
        "ProductID": "INTEGER",
        "CustomerID": "INTEGER",
        "Rating": "INTEGER",
        "ReviewText": "STRING",
        "ReviewDate": "TIMESTAMP"
    },
    "Products": {
        "ProductID": "INTEGER",
        "ProductName": "STRING",
        "Description": "STRING",
        "Category": "STRING",
        "Price": "FLOAT",
        "SKU": "STRING",
        "StockQuantity": "INTEGER"
    }
}

def get_default_prompt_template():
    """Get the default prompt template, first trying GCS then falling back to local"""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(PROMPT_BUCKET_NAME)
        latest_blob = max(
            bucket.list_blobs(prefix="prompts/"), 
            key=lambda x: x.name
        )
        return json.loads(latest_blob.download_as_text())
    except Exception:
        # Fallback to default if GCS access fails
        return {
            "version": "1.0.0",
            "template": """Convert this English question into an accurate **BigQuery SQL query**.

            **BigQuery Schema:**
            {schema}

            **Dataset:** `{project_id}.{dataset_id}`

            **User Query:** "{user_query}"

            **Rules:**
            1. Use exact column and table names as in the schema.
            2. Always include `{project_id}.{dataset_id}.table_name` format in FROM clauses.
            3. Do NOT use `sql` or markdown formatting in the output.
            4. Ensure SQL is formatted for Google BigQuery.
            5. If aggregating data, use `GROUP BY` correctly.

            Return **ONLY** the SQL query.""",
            "metadata": {
                "description": "Basic SQL generation prompt",
                "author": "test",
                "created_at": "2024-01-01"
            }
        }

# Dynamic template that updates from GCS
EXPECTED_PROMPT_TEMPLATE = get_default_prompt_template()