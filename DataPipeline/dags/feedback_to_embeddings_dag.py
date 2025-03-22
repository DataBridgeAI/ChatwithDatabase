from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
# from feedback_helper import process_and_store_embeddings
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from feedback_helper import fetch_user_queries, generate_query_embeddings, zip_directory, upload_zip_to_gcs

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 15),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'feedback_embeddings_dag',
    default_args=default_args,
    description='Fetch feedback, generate embeddings, zip and upload to GCS',
    schedule_interval=timedelta(hours=6),
    catchup=False,
)

fetch_queries_task = PythonOperator(
    task_id='fetch_user_queries',
    python_callable=fetch_user_queries,
    dag=dag,
)

generate_embeddings_task = PythonOperator(
    task_id='generate_query_embeddings',
    python_callable=generate_query_embeddings,
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
    slack_webhook_conn_id='slack_webhook',  # Use this instead of http_conn_id
    message="✅ Airflow DAG `feedback_embeddings_dag` completed successfully!",
    channel="#airflow-notifications",
    username="airflow-bot",
    dag=dag
    )

fetch_queries_task >> generate_embeddings_task >> zip_task >> upload_task >> send_slack_notification
