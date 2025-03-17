from detoxify import Detoxify

def block_inappropriate_query(user_query):
    """Block inappropriate queries."""
    toxic_keywords = ["violence", "illegal", "fake", "prohibited"]
    
    if any(word in user_query.lower() for word in toxic_keywords):
        return "Inappropriate query detected."
    return None


def check_sql_safety(user_query):
    """Ensure SQL safety by checking for harmful SQL commands."""
    sql_blacklist = ["DROP", "DELETE", "ALTER", "INSERT", "TRUNCATE", "UPDATE"]  # Add more keywords if necessary
    
    # Case-insensitive check for blacklisted SQL commands
    if any(word in user_query.upper() for word in sql_blacklist):
        return "Restricted SQL operation detected."
    
    return None

def is_toxic(query: str) -> bool:
    """Check if the query contains toxic language."""
    toxicity_score = Detoxify('original').predict(query)["toxicity"]
    return toxicity_score > 0.7  # Threshold (can be adjusted)

def validate_query(user_query: str) -> str:
    """Validate query for toxicity and SQL safety."""
    # First, check if the query contains inappropriate content or toxic language
    toxic_error = block_inappropriate_query(user_query)
    if toxic_error:
        return toxic_error

    # Then, check for SQL safety issues
    sql_error = check_sql_safety(user_query)
    if sql_error:
        return sql_error

    # Finally, check if the query is toxic
    if is_toxic(user_query):
        return "🚫 Query contains harmful language. Please modify your input."

    return None  # No issues detected, query is safe
