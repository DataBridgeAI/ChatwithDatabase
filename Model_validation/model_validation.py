# from google.cloud import bigquery
# from sklearn.metrics import precision_score, recall_score, f1_score
# import pandas as pd

# # Configuration
# PROJECT_ID = "chatwithdata-451800"
# FEEDBACK_DATASET_ID = "Feedback_Dataset"  # Corrected to Feedback_Dataset
# RETAIL_DATASET_ID = "RetailDataset"  # The dataset where actual data tables are stored
# MODEL_VALIDATION_TABLE_ID = "Model_Validation"  # Existing table where generated and correct SQL are stored

# # Initialize BigQuery Client
# client = bigquery.Client(project=PROJECT_ID)

# def fetch_evaluation_data():
#     """Fetch generated SQL, correct SQL, and feedback from BigQuery."""
#     query = f"""
#     SELECT generated_sql, correct_sql, feedback
#     FROM `{PROJECT_ID}.{FEEDBACK_DATASET_ID}.{MODEL_VALIDATION_TABLE_ID}`
#     WHERE correct_sql IS NOT NULL
#     """
#     return client.query(query).to_dataframe()

# def execute_query(sql):
#     """Execute SQL query on BigQuery and return results as a DataFrame."""
#     try:
#         query_job = client.query(sql)
#         return query_job.to_dataframe()
#     except Exception as e:
#         print(f"Query Execution Error: {e}")
#         return None

# def evaluate_model():
#     """Evaluate chatbot-generated SQL against expected SQL using query results."""
#     df = fetch_evaluation_data()

#     if df.empty:
#         print("No evaluation data found.")
#         return

#     precision_scores, recall_scores, f1_scores = [], [], []

#     for _, row in df.iterrows():
#         generated_sql = row["generated_sql"]
#         correct_sql = row["correct_sql"]

#         # Execute both queries
#         generated_result = execute_query(generated_sql)
#         correct_result = execute_query(correct_sql)

#         if generated_result is None or correct_result is None:
#             print(f"Skipping query due to execution error: {generated_sql}")
#             continue

#         # Convert results to comparable format
#         generated_result = generated_result.applymap(str)  # Convert all values to string
#         correct_result = correct_result.applymap(str)

#         # Ensure column order is the same
#         generated_result = generated_result[sorted(generated_result.columns)]
#         correct_result = correct_result[sorted(correct_result.columns)]

#         # Check if both results have the same structure
#         if generated_result.shape != correct_result.shape:
#             print(f"Skipping query due to mismatched result shape: {generated_sql}")
#             continue

#         # Convert DataFrames to sets of tuples for easier comparison
#         generated_set = set(generated_result.itertuples(index=False, name=None))
#         correct_set = set(correct_result.itertuples(index=False, name=None))

#         # Calculate Precision, Recall, F1-score
#         tp = len(generated_set & correct_set)  # True Positives (Correct Matches)
#         fp = len(generated_set - correct_set)  # False Positives (Extra Rows)
#         fn = len(correct_set - generated_set)  # False Negatives (Missing Rows)

#         precision = tp / (tp + fp) if (tp + fp) > 0 else 0
#         recall = tp / (tp + fn) if (tp + fn) > 0 else 0
#         f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

#         precision_scores.append(precision)
#         recall_scores.append(recall)
#         f1_scores.append(f1)

#     # Compute overall metrics
#     overall_precision = sum(precision_scores) / len(precision_scores) if precision_scores else 0
#     overall_recall = sum(recall_scores) / len(recall_scores) if recall_scores else 0
#     overall_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0

#     print(f"\n📊 Model Evaluation Metrics:")
#     print(f"✅ Precision: {overall_precision:.2f}")
#     print(f"✅ Recall: {overall_recall:.2f}")
#     print(f"✅ F1-Score: {overall_f1:.2f}")

#     return overall_precision, overall_recall, overall_f1

# if __name__ == "__main__":
#     evaluate_model()

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
