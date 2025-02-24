from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from scripts.schema_drift_checker import check_schema_drift, update_embeddings
import json
import redis

def detect_schema_drift(**kwargs):
    """Detects if the schema in BigQuery has changed."""
    schema_changed = check_schema_drift()
    if schema_changed:
        return "update_embeddings_task"
    return "skip_update"

def update_schema_embeddings(**kwargs):
    """Updates schema embeddings and stores them in Redis."""
    new_embeddings = update_embeddings()
    redis_client = redis.Redis(host='redis', port=6379, db=0)
    redis_client.set('latest_schema_embeddings', json.dumps(new_embeddings))
    return "Schema embeddings updated."

def skip_update(**kwargs):
    return "No schema drift detected. Skipping update."

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 2, 22),
    'retries': 1
}

dag = DAG(
    'schema_drift_detection_dag',
    default_args=default_args,
    description='Detects schema drift and updates schema embeddings if necessary',
    schedule_interval='@daily'
)

detect_drift_task = PythonOperator(
    task_id='detect_schema_drift',
    python_callable=detect_schema_drift,
    provide_context=True,
    dag=dag
)

update_embeddings_task = PythonOperator(
    task_id='update_embeddings_task',
    python_callable=update_schema_embeddings,
    provide_context=True,
    dag=dag
)

skip_update_task = PythonOperator(
    task_id='skip_update',
    python_callable=skip_update,
    provide_context=True,
    dag=dag
)

detect_drift_task >> [update_embeddings_task, skip_update_task]
