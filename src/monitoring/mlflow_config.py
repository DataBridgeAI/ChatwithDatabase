import mlflow
import os
from datetime import datetime

# MLflow tracking URI - using local filesystem
MLFLOW_TRACKING_URI = "file:./mlruns"  # Changed to use local filesystem
EXPERIMENT_NAME = "sql_generation_tracking"

def setup_mlflow():
    """Initialize MLflow configuration"""
    # Set the tracking URI
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    
    # Get or create the experiment
    try:
        # First try to get existing experiment
        experiment = mlflow.get_experiment_by_name(EXPERIMENT_NAME)
        if experiment is None:
            # Create new experiment if it doesn't exist
            experiment_id = mlflow.create_experiment(
                EXPERIMENT_NAME,
                tags={"version": "1.0", "env": os.getenv("ENVIRONMENT", "development")}
            )
        else:
            experiment_id = experiment.experiment_id
    except Exception as e:
        print(f"Error setting up MLflow: {str(e)}")
        experiment_id = 0  # Use default experiment if there's an error
    
    mlflow.set_experiment(EXPERIMENT_NAME)
    return experiment_id

def log_query_generation(
    user_query: str,
    generated_sql: str,
    execution_time: float,
    feedback: str = None,
    error: str = None,
    similar_query_found: bool = False,
    metadata: dict = None
):
    """Log query generation details to MLflow"""
    try:
        with mlflow.start_run(run_name=f"query_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            # Log parameters
            params = {
                "model": "gpt-4",
                "temperature": 0.3,
                "similar_query_found": similar_query_found
            }
            if metadata:
                params.update(metadata)
            mlflow.log_params(params)
            
            # Log metrics
            metrics = {
                "execution_time": execution_time,
                "query_length": len(user_query),
                "sql_length": len(generated_sql)
            }
            
            # Add feedback score if provided
            if feedback is not None:
                metrics["feedback_score"] = 1.0 if feedback == "👍 Yes" else 0.0 if feedback == "👎 No" else -1.0
            
            mlflow.log_metrics(metrics)
            
            # Log query details as text artifact
            artifact_path = os.path.join(os.getcwd(), "query_details.txt")
            with open(artifact_path, "w") as f:
                f.write(f"User Query: {user_query}\n")
                f.write(f"Generated SQL: {generated_sql}\n")
                if error:
                    f.write(f"Error: {error}\n")
            
            mlflow.log_artifact(artifact_path)
            if os.path.exists(artifact_path):
                os.remove(artifact_path)
            
            # Log tags
            mlflow.set_tags({
                "query_type": "similar" if similar_query_found else "new",
                "status": "error" if error else "success"
            })
    except Exception as e:
        print(f"Error logging to MLflow: {str(e)}")
