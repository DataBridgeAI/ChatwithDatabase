# schema_data_drift.py
from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from scripts.drift_helper import check_schema_drift, check_data_drift, send_slack_alert

# Constants
SLACK_CONN_ID = "slack_webhook"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "monitor_drift",
    default_args=default_args,
    description="Detect schema drift, data drift, and notify via Slack",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 3, 1),
    catchup=False,
    tags=["nlsql", "monitoring"],
)

check_schema_drift_task = PythonOperator(
    task_id="check_schema_drift",
    python_callable=check_schema_drift,
    provide_context=True,
    dag=dag,
)

check_data_drift_task = PythonOperator(
    task_id="check_data_drift",
    python_callable=check_data_drift,
    provide_context=True,
    dag=dag,
)

send_slack_alert_task = PythonOperator(
    task_id="send_slack_alert",
    python_callable=send_slack_alert,
    provide_context=True,
    dag=dag,
)

check_schema_drift_task >> check_data_drift_task >> send_slack_alert_task
