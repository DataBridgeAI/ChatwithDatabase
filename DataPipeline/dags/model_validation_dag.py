from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from datetime import datetime, timedelta
from Model_validation.model_validation import evaluate_model

# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG
with DAG(
    'model_validation_weekly',
    default_args=default_args,
    description='Weekly model performance validation',
    schedule_interval='0 0 * * 0',  # Run at midnight every Sunday
    start_date=datetime(2025, 3, 1),
    catchup=False,
    tags=['model', 'validation']
) as dag:

    # Task 1: Run model validation
    run_model_validation = PythonOperator(
        task_id='run_model_validation',
        python_callable=evaluate_model,
        dag=dag
    )

    # Task 2: Send Slack notification
    send_slack_notification = SlackWebhookOperator(
        task_id='send_slack_notification',
        slack_webhook_conn_id='slack_webhook',
        message="✅ Weekly Model Evaluation Completed. Check BigQuery for results.",
        channel="#airflow-notifications",
        username="airflow-bot",
        dag=dag
    )

    # Set dependencies
    run_model_validation >> send_slack_notification
