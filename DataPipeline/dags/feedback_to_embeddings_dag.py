from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from scripts.feedback_helper import fetch_user_queries, update_query_embeddings, zip_directory, upload_zip_to_gcs

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 15),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'pool': 'embedding_pool',  # Create this pool in Airflow UI
    'max_active_runs': 1
}

dag = DAG(
    'feedback_embeddings_dag',
    default_args=default_args,
    description='Update embeddings with feedback from last 24 hours',
    schedule_interval=timedelta(hours=6),
    catchup=False,
    concurrency=1  # Ensure only one task runs at a time
)

def fetch_and_update_embeddings(**context):
    try:
        # Fetch queries from last 24 hours
        recent_queries = fetch_user_queries(hours=24)
        
        # Store count for logging
        context['task_instance'].xcom_push(key='new_queries_count', value=len(recent_queries))
        
        # Update embeddings with new queries
        update_query_embeddings(recent_queries)
    except Exception as e:
        print(f"Error in fetch_and_update_embeddings: {str(e)}")
        raise

fetch_and_update_task = PythonOperator(
    task_id='fetch_and_update_embeddings',
    python_callable=fetch_and_update_embeddings,
    provide_context=True,
    dag=dag,
)

zip_task = PythonOperator(
    task_id='zip_directory',
    python_callable=zip_directory,
    dag=dag,
)

upload_task = PythonOperator(
    task_id='upload_zip_to_gcs',
    python_callable=upload_zip_to_gcs,
    dag=dag,
)

send_slack_notification = SlackWebhookOperator(
    task_id='send_slack_notification',
    slack_webhook_conn_id='slack_webhook',
    message="✅ Airflow DAG `feedback_embeddings_dag` completed successfully!",
    channel="#airflow-notifications",
    username="airflow-bot",
    dag=dag
)

# Define task dependencies
fetch_and_update_task >> zip_task >> upload_task >> send_slack_notification