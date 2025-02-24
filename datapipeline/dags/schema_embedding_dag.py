# from airflow import DAG
# from airflow.operators.python import PythonOperator
# from datetime import datetime
# from scripts.generate_schema_embeddings import generate_schema_embeddings

# default_args = {
#     "owner": "airflow",
#     "start_date": datetime(2025, 2, 21),
#     "retries": 1,
# }

# dag = DAG(
#     "schema_embedding_pipeline",
#     default_args=default_args,
#     schedule_interval="@daily",  # Run daily
#     catchup=False,
# )

# generate_embeddings_task = PythonOperator(
#     task_id="generate_schema_embeddings",
#     python_callable=generate_schema_embeddings,
#     dag=dag,
# )

# generate_embeddings_task
