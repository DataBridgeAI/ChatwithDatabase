"""Configuration settings for model validation"""

# GCP Configuration
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
PROMPT_BUCKET_NAME = "sql-prompts-store"

# Schema Configuration
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

EXPECTED_PROMPT_TEMPLATE = {
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
