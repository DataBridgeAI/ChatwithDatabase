from mlflow_config import QueryTracker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_experiments():
    # Initialize tracker
    tracker = QueryTracker()
    
    # Create some test experiments
    test_queries = [
        ("Show me sales by region", "SELECT region, SUM(sales) FROM sales GROUP BY region"),
        ("Top 10 customers", "SELECT customer_id, total_spend FROM customers ORDER BY total_spend DESC LIMIT 10"),
        ("Monthly revenue", "SELECT DATE_TRUNC(date, MONTH) as month, SUM(revenue) FROM transactions GROUP BY month")
    ]
    
    for user_query, sql in test_queries:
        tracker.log_query_execution(
            user_query=user_query,
            generated_sql=sql,
            execution_time=0.5,
            total_time=1.0,
            metadata={"test": True}
        )
        logger.info(f"Created experiment for query: {user_query}")

if __name__ == "__main__":
    create_test_experiments()
    print("Test experiments created. Check MLflow UI at http://localhost:5001")