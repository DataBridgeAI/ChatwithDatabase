from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.models import Variable
from datetime import timedelta, datetime

# Import the processing functions
from schema_embeddings_processor import (
    generate_and_store_embeddings,
    get_all_datasets,
    PROJECT_ID
)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'pool': 'embedding_pool',  # Create this pool in Airflow UI
    'max_active_runs': 1
}

# Define the DAG
with DAG(
    dag_id="schema_embeddings_dag",
    default_args=default_args,
    description='Generate and store schema embeddings for all datasets',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 3, 1),
    catchup=False,
    tags=['schema', 'embeddings']
) as dag:
    
    def process_datasets(**context):
        """Process all datasets and store their embeddings."""
        try:
            success = generate_and_store_embeddings()
            if not success:
                raise Exception("Failed to generate and store embeddings")
            
            # Get count of processed datasets for logging
            datasets = get_all_datasets(PROJECT_ID)
            context['task_instance'].xcom_push(
                key='processed_datasets_count', 
                value=len(datasets)
            )
            return success
        except Exception as e:
            print(f"Error in process_datasets: {str(e)}")
            raise
    
    # Task 1: Generate and store embeddings for all datasets
    generate_embeddings_task = PythonOperator(
        task_id="generate_and_store_embeddings",
        python_callable=process_datasets,
        provide_context=True,
        dag=dag
    )
    
    def get_slack_message(**context):
        """Generate success message with dataset count."""
        try:
            datasets_count = context['task_instance'].xcom_pull(
                task_ids='generate_and_store_embeddings',
                key='processed_datasets_count'
            )
            return (f"✅ Schema embeddings generation completed successfully!\n"
                   f"Processed {datasets_count} datasets in project {PROJECT_ID}")
        except Exception:
            return "✅ Schema embeddings generation completed successfully!"

    # Task 2: Send Slack notification
    send_slack_notification = SlackWebhookOperator(
        task_id='send_slack_notification',
        slack_webhook_conn_id='slack_webhook',
        message=get_slack_message,
        channel="#airflow-notifications",
        username="airflow-bot",
        dag=dag
    )

    # Define task dependencies
    generate_embeddings_task >> upload_to_gcs_task >> send_slack_notification
