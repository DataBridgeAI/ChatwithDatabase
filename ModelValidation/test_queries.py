"""Test queries for validation and bias checking"""

TEST_QUERIES = [
    "Show me total sales by product category",
    # "Find customers who have made more than 5 orders",
    # "List all products with less than 10 items in stock",
    # "What are the top-rated products based on reviews?",
    # "Calculate average order value per customer",
    # "Show me orders with total amount greater than $1000",
    # "List all customers from California",
    # "Find products that have never been ordered",
    # "Show me the most recent product reviews",
    # "Calculate total revenue by product category"
]

# Expected SQL results for validation
EXPECTED_SQL_RESULTS = {
    "Show me total sales by product category": """
    SELECT 
        p.Category,
        SUM(oi.Quantity * oi.UnitPrice) as total_sales
    FROM `chatwithdata-451800.RetailDataset.Products` p
    JOIN `chatwithdata-451800.RetailDataset.OrderItems` oi ON p.ProductID = oi.ProductID
    GROUP BY p.Category
    """,
    
    "Find customers who have made more than 5 orders": """
    SELECT 
        c.CustomerID,
        c.FirstName,
        c.LastName,
        COUNT(o.OrderID) as order_count
    FROM `chatwithdata-451800.RetailDataset.Customers` c
    JOIN `chatwithdata-451800.RetailDataset.Orders` o ON c.CustomerID = o.CustomerID
    GROUP BY c.CustomerID, c.FirstName, c.LastName
    HAVING COUNT(o.OrderID) > 5
    """
}

# Queries that should trigger bias detection (for testing)
BIAS_TEST_QUERIES = [
    "Show sales data filtered by customer gender"
    # "Compare orders between young and elderly customers",
    # "List customers by ethnicity",
    # "Show products popular among female customers",
    # "Compare spending patterns between men and women"
]
