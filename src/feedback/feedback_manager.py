# feedback_manager.py - Stores user feedback in BigQuery
import google.cloud.bigquery as bigquery

def store_feedback(user_question: str, generated_sql: str, feedback: str):
    client = bigquery.Client()
    table_id = "chatwithdata-451800.Feedback_Dataset.user_feedback"
    
    if feedback == "👍 Yes":
        numeric_feedback = '1'
    elif feedback == "👎 No":
        numeric_feedback = '0'
    else:
        numeric_feedback = None # or some other value for unknown feedback
    
    rows_to_insert = [{
        "user_question": user_question,
        "generated_sql": generated_sql,
        "feedback": numeric_feedback
    }]
    
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print("Error inserting feedback:", errors)
    else:
        print("Feedback stored successfully.")
