# from airflow import DAG
# from airflow.operators.python import PythonOperator
# from datetime import datetime
# from scripts.query_processing import process_user_query

# default_args = {
#     "owner": "airflow",
#     "start_date": datetime(2025, 2, 21),
#     "retries": 1,
# }

# dag = DAG(
#     "text_to_sql_pipeline",
#     default_args=default_args,
#     schedule_interval=None,  # Triggered on demand
#     catchup=False,
# )

# process_query_task = PythonOperator(
#     task_id="process_user_query",
#     python_callable=process_user_query,
#     op_args=["{{ dag_run.conf['user_query'] }}"],  # Passing user query dynamically
#     dag=dag,
# )

# process_query_task


from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from scripts.query_preprocessor import check_toxicity, check_relevance
# from scripts.embedding_generator import fetch_schema_embeddings, retrieve_relevant_schema
from scripts.query_preprocessor import retrieve_relevant_schema
import json
import redis

def process_user_query(**kwargs):
    user_query = kwargs['dag_run'].conf.get('user_query', '')
    redis_client = redis.Redis(host='redis', port=6379, db=0)
    
    # Step 1: Toxicity and Security Check
    if not check_toxicity(user_query):
        redis_client.set('latest_response', json.dumps({"message": "Sorry, I can't answer this question."}))
        return "Query rejected due to toxicity."
    
    # Step 3: Schema Retrieval
    
    relevant_schema = retrieve_relevant_schema(user_query)
    if not relevant_schema:
        redis_client.set('latest_response', json.dumps({"message": "Sorry, I can't answer this question."}))
        return "No relevant schema found."
    
    # Step 4: Store Retrieved Schema for Fast Access
    redis_client.set('latest_schema', json.dumps(relevant_schema))
    redis_client.set('latest_response', json.dumps({"message": "Query processed successfully.", "schema": relevant_schema}))
    
    return "Query processing completed."

def store_error_message(**kwargs):
    redis_client = redis.Redis(host='redis', port=6379, db=0)
    redis_client.set('latest_response', json.dumps({"message": "Sorry, I can't answer this question."}))
    return "Stored error message in Redis."

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 2, 22),
    'retries': 1
}

dag = DAG(
    'query_processing_dag',
    default_args=default_args,
    description='Processes user query: toxicity check, relevance check, schema retrieval',
    schedule_interval=None  # Triggered by user input
)

process_query_task = PythonOperator(
    task_id='process_user_query',
    python_callable=process_user_query,
    provide_context=True,
    dag=dag
)

store_error_task = PythonOperator(
    task_id='store_error_message',
    python_callable=store_error_message,
    dag=dag
)

process_query_task >> store_error_task
