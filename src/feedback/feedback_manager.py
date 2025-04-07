# feedback_manager.py - Stores user feedback in BigQuery
import google.cloud.bigquery as bigquery
from datetime import datetime

def store_feedback(user_question: str, generated_sql: str, feedback: str, execution_success: bool = True):
    client = bigquery.Client()
    table_id = "chatwithdata-451800.Feedback_Dataset.user_feedback"
    
    if feedback == "👍 Yes":
        numeric_feedback = '1'
    elif feedback == "👎 No":
        numeric_feedback = '0'
    else:
        numeric_feedback = None
    
    # Convert datetime to string in ISO format
    current_time = datetime.now().isoformat()
    
    rows_to_insert = [{
        "user_question": user_question,
        "generated_sql": generated_sql,
        "feedback": numeric_feedback,
        "timestamp": current_time,  # Use ISO format string instead of datetime object
        "execution_success": execution_success,
        "query_type": detect_query_type(generated_sql)
    }]
    
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print("Error inserting feedback:", errors)
    else:
        print("Feedback stored successfully.")

def detect_query_type(sql: str) -> str:
    # Implement query type detection logic here
    # This is a placeholder implementation
    if "SELECT" in sql:
        return "SELECT"
    elif "INSERT" in sql:
        return "INSERT"
    elif "UPDATE" in sql:
        return "UPDATE"
    elif "DELETE" in sql:
        return "DELETE"
    else:
        return "UNKNOWN"
