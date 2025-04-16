from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from datetime import datetime, timedelta
import sys
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# # Add the project root to Python path
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
# sys.path.append(project_root)

from PromptValidation.prompt_learning import PromptLearning
from PromptValidation.config import get_default_prompt_template
import importlib

def update_prompt_based_on_feedback():
    """Update prompt template based on feedback analysis"""
    try:
        logger.info("Starting prompt learning pipeline")
        prompt_learning = PromptLearning()
        
        # Analyze recent feedback
        logger.info("Analyzing feedback from last 24 hours")
        feedback_analysis = prompt_learning.analyze_feedback(time_window_hours=24)
        logger.info(f"Feedback analysis results: {feedback_analysis}")
        
        # If success rate is below threshold, generate new rules
        current_success_rate = feedback_analysis["success_rate"]
        threshold = prompt_learning.performance_threshold
        logger.info(f"Current success rate: {current_success_rate:.2f}, Threshold: {threshold}")
        
        if current_success_rate < threshold:
            logger.info(f"Success rate below threshold. Generating new rules...")
            failed_queries = feedback_analysis["failed_queries"]
            logger.info(f"Number of failed queries to analyze: {len(failed_queries)}")
            
            new_rules = prompt_learning.generate_new_rules(failed_queries)
            logger.info(f"Generated {len(new_rules)} new rules")
            
            logger.info("Updating prompt template with new rules")
            new_template, version_id = prompt_learning.update_prompt_template(new_rules)
            logger.info(f"New prompt template version created: {version_id}")
            
            # Force reload of config module to get updated template
            logger.info("Reloading config module with new template")
            importlib.reload(importlib.import_module('PromptValidation.config'))
            
            return {
                "updated": True,
                "new_rules": new_rules,
                "version_id": version_id,
                "success_rate": current_success_rate,
                "analyzed_queries": len(failed_queries)
            }
        
        logger.info("Success rate above threshold, no updates needed")
        return {
            "updated": False,
            "success_rate": current_success_rate,
            "analyzed_queries": len(feedback_analysis.get("failed_queries", []))
        }
        
    except Exception as e:
        logger.error(f"Error in prompt learning pipeline: {str(e)}", exc_info=True)
        raise

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': lambda context: logger.error(f"Task failed: {context['task_instance'].task_id}")
}

dag = DAG(
    'prompt_learning_dag',
    default_args=default_args,
    description='Update prompt based on feedback analysis',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

update_task = PythonOperator(
    task_id='update_prompt',
    python_callable=update_prompt_based_on_feedback,
    dag=dag,
)

# Enhanced Slack message with more details
notify_slack = SlackWebhookOperator(
    task_id='notify_slack',
    slack_webhook_conn_id='slack_webhook',
    message="""
    🤖 *Prompt Learning Pipeline Complete*
    
    📝 *Status*:
    • Updated: {{ task_instance.xcom_pull(task_ids='update_prompt')['updated'] }}
    
    {% if task_instance.xcom_pull(task_ids='update_prompt')['updated'] %}
    🆕 *Updates*:
    • Version ID: {{ task_instance.xcom_pull(task_ids='update_prompt')['version_id'] }}
    
    📋 *New Rules*:
    {% for rule in task_instance.xcom_pull(task_ids='update_prompt')['new_rules'] %}
    • {{ rule }}
    {% endfor %}
    {% endif %}
    
    """,
    dag=dag,
)

# Log task dependencies
logger.info("Setting up task dependencies")
update_task >> notify_slack

# Log DAG initialization
logger.info("Prompt learning DAG initialized successfully")