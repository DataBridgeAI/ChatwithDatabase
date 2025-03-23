import pytest
from ModelValidation.prompt_validator import PromptValidator
from ModelValidation.config import PROJECT_ID, DATASET_ID, RETAIL_SCHEMA

@pytest.fixture
def validator():
    return PromptValidator(PROJECT_ID, "sql-prompts-store")

def test_sql_validation(validator):

    valid_sql = """
    SELECT p.ProductName, SUM(oi.Quantity) as total_sold
    FROM `chatwithdata-451800.RetailDataset.Products` p
    JOIN `chatwithdata-451800.RetailDataset.OrderItems` oi ON p.ProductID = oi.ProductID
    GROUP BY p.ProductName
    """
    is_valid, message = validator.validate_sql_correctness(valid_sql)
    assert is_valid
    
    # Invalid SQL
    invalid_sql = "SELECT * FROM Products WHERE stuff"
    is_valid, message = validator.validate_sql_correctness(invalid_sql)
    assert not is_valid

def test_prompt_template_validation(validator):
    # Valid template with actual schema
    valid_template = """
    Given the schema {schema} for project {project_id}.{dataset_id},
    generate a SQL query for: {user_query}
    Using tables: Customers, Orders, OrderItems, Products, ProductReviews
    """
    is_valid, issues = validator.validate_prompt_template(valid_template)
    assert is_valid
    assert not issues
    
    # Invalid template
    invalid_template = "Generate SQL for: {user_query}"
    is_valid, issues = validator.validate_prompt_template(invalid_template)
    assert not is_valid
    assert len(issues) > 0

def test_schema_validation():
    # Test that all required tables exist in schema
    required_tables = ["Customers", "Orders", "OrderItems", "Products", "ProductReviews"]
    for table in required_tables:
        assert table in RETAIL_SCHEMA

def test_table_structure():
    # Test specific column existence and types
    assert "CustomerID" in RETAIL_SCHEMA["Customers"]
    assert RETAIL_SCHEMA["Customers"]["CustomerID"] == "INTEGER"
    assert "OrderDate" in RETAIL_SCHEMA["Orders"]
    assert RETAIL_SCHEMA["Orders"]["OrderDate"] == "TIMESTAMP"

