from google.cloud import bigquery
from sklearn.metrics import precision_score, recall_score, f1_score
from datetime import datetime
import pandas as pd

# Configuration
PROJECT_ID = "chatwithdata-451800"
FEEDBACK_DATASET_ID = "Feedback_Dataset"
MODEL_VALIDATION_TABLE_ID = "Model_Validation"
METRICS_TABLE_ID = "Model_Performance_Metrics"

# Initialize BigQuery Client
client = bigquery.Client(project=PROJECT_ID)

def fetch_evaluation_data():
    """Fetch generated SQL, correct SQL, and feedback from BigQuery."""
    query = f"""
    SELECT generated_sql, correct_sql, feedback
    FROM `{PROJECT_ID}.{FEEDBACK_DATASET_ID}.{MODEL_VALIDATION_TABLE_ID}`
    WHERE feedback IS NOT NULL
    """
    return client.query(query).to_dataframe()

def store_metrics_in_bigquery(metrics):
    """Store model evaluation metrics in BigQuery."""
    table_id = f"{PROJECT_ID}.{FEEDBACK_DATASET_ID}.{METRICS_TABLE_ID}"

    # Ensure table exists
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS `{table_id}` (
        timestamp TIMESTAMP,
        precision FLOAT64,
        recall FLOAT64,
        f1_score FLOAT64,
        total_samples INT64,
        correct_predictions INT64,
        incorrect_predictions INT64
    )
    """
    client.query(create_table_query).result()

    # Insert computed metrics
    rows_to_insert = [metrics]
    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        raise Exception(f"Error inserting rows: {errors}")

def evaluate_and_store_metrics():
    """Evaluate model performance and store results in BigQuery."""
    df = fetch_evaluation_data()

    if df.empty:
        print("No evaluation data found.")
        return

    y_true = [1] * len(df)  # All examples should be correct
    y_pred = df['feedback'].astype(int).tolist()  # Convert feedback to binary

    # Compute metrics
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    metrics = {
        'timestamp': datetime.utcnow().isoformat(),
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'total_samples': len(df),
        'correct_predictions': sum(y_pred),
        'incorrect_predictions': len(y_pred) - sum(y_pred)
    }

    print(f"\n📊 Model Evaluation Metrics:")
    print(f"✅ Precision: {precision:.2f}")
    print(f"✅ Recall: {recall:.2f}")
    print(f"✅ F1-Score: {f1:.2f}")

    store_metrics_in_bigquery(metrics)

if __name__ == "__main__":
    evaluate_and_store_metrics()