from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from datetime import datetime, timedelta
import json

# Import the analysis functions from the scripts folder
from bias_analysis import (
    analyze_schema_coverage,
    analyze_query_distribution,
    analyze_demographic_bias,
    analyze_execution_failures
)

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 3, 15),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'bias_detection_dag',
    default_args=default_args,
    description='Detect bias in SQL query generation',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

def process_and_format_results(**context):
    """Process analysis results and create a formatted summary."""
    task_ids = ['analyze_schema_coverage', 'analyze_query_distribution', 
                'analyze_demographic_bias', 'analyze_execution_failures']
    
    summary = {}
    for task_id in task_ids:
        results = context['task_instance'].xcom_pull(task_ids=task_id)
        summary[task_id] = results

    # Create a formatted message for Slack
    message = "✅ Bias Detection Analysis Summary:\n\n"
    
    # Schema Coverage
    message += "*Schema Coverage*\n"
    for item in summary['analyze_schema_coverage']:
        message += f"- Table `{item['table_name']}`: {item['usage_count']} queries\n"
    
    # Query Distribution
    message += "\n*Query Distribution*\n"
    for item in summary['analyze_query_distribution']:
        message += f"- Condition `{item['filter_condition']}`: {item['filter_count']} occurrences\n"
    
    # Demographic Bias
    message += "\n*Demographic Analysis*\n"
    for item in summary['analyze_demographic_bias']:
        message += f"- {item['demographic_filter']}: {item['usage_count']} queries\n"
    
    # Execution Failures
    message += "\n*Execution Failures*\n"
    for item in summary['analyze_execution_failures']:
        message += f"- {item['query_type']}: {item['failure_count']} failures (Success rate: {item['success_rate']:.2%})\n"
    
    return message

schema_coverage_task = PythonOperator(
    task_id='analyze_schema_coverage',
    python_callable=analyze_schema_coverage,
    dag=dag,
)

query_distribution_task = PythonOperator(
    task_id='analyze_query_distribution',
    python_callable=analyze_query_distribution,
    dag=dag,
)

demographic_bias_task = PythonOperator(
    task_id='analyze_demographic_bias',
    python_callable=analyze_demographic_bias,
    dag=dag,
)

execution_failures_task = PythonOperator(
    task_id='analyze_execution_failures',
    python_callable=analyze_execution_failures,
    dag=dag,
)

format_results_task = PythonOperator(
    task_id='format_results',
    python_callable=process_and_format_results,
    provide_context=True,
    dag=dag,
)

notify_slack = SlackWebhookOperator(
    task_id='send_slack_notification',
    slack_webhook_conn_id='slack_webhook',
    message="{{ task_instance.xcom_pull(task_ids='format_results') }}",
    channel="#airflow-notifications",
    username="airflow-bot",
    dag=dag
)

[schema_coverage_task, query_distribution_task, demographic_bias_task, execution_failures_task] >> format_results_task >> notify_slack
