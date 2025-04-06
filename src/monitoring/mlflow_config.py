import mlflow
import os
from datetime import datetime
import sqlparse
from typing import Dict, Any, Optional
import time

class QueryTracker:
    def __init__(self):
        self.MLFLOW_TRACKING_URI = "file:./mlruns"
        self.EXPERIMENT_NAME = "sql_execution_tracking"
        self.setup_mlflow()

    def setup_mlflow(self):
        """Initialize MLflow configuration"""
        mlflow.set_tracking_uri(self.MLFLOW_TRACKING_URI)
        
        try:
            experiment = mlflow.get_experiment_by_name(self.EXPERIMENT_NAME)
            if experiment is None:
                self.experiment_id = mlflow.create_experiment(
                    self.EXPERIMENT_NAME,
                    tags={"version": "1.0", "env": os.getenv("ENVIRONMENT", "development")}
                )
            else:
                self.experiment_id = experiment.experiment_id
            
            mlflow.set_experiment(self.EXPERIMENT_NAME)
        except Exception as e:
            print(f"Error setting up MLflow: {str(e)}")
            self.experiment_id = 0

    def log_query_execution(
        self,
        user_query: str,
        generated_sql: str,
        execution_time: float,
        total_time: float,
        query_result: Optional[Any] = None,
        error: Optional[str] = None,
        feedback: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log comprehensive query execution details including latency"""
        try:
            formatted_sql = sqlparse.format(
                generated_sql,
                reindent=True,
                keyword_case='upper'
            ) if generated_sql else ""
            
            run_name = f"query_exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            with mlflow.start_run(run_name=run_name):
                # Log parameters
                params = {
                    "model": "gpt-4",
                    "temperature": 0.3,
                }
                if metadata:
                    params.update(metadata)
                mlflow.log_params(params)
                
                # Calculate metrics including latency
                latency = max(0.0, total_time - execution_time)  # Ensure non-negative
                metrics = {
                    "bigquery_execution_time": execution_time,  # Actual BigQuery execution time
                    "total_processing_time": total_time,        # Total time including LLM
                    "latency": latency,                         # Network/processing overhead
                    "query_length": len(user_query),
                    "sql_length": len(formatted_sql),
                }
                
                if formatted_sql:
                    metrics.update({
                        "table_count": self._count_tables(formatted_sql),
                        "join_count": self._count_joins(formatted_sql),
                        "where_conditions": self._count_where_conditions(formatted_sql),
                    })
                
                if query_result is not None:
                    if hasattr(query_result, '__len__'):
                        metrics["result_row_count"] = len(query_result)
                    if hasattr(query_result, 'columns'):
                        metrics["result_column_count"] = len(query_result.columns)
                
                mlflow.log_metrics(metrics)
                
                # Log tags
                tags = {
                    "status": "error" if error else "success",
                    "performance": self._categorize_performance(execution_time),
                    "latency_category": self._categorize_latency(latency)
                }
                
                if feedback:
                    tags["feedback"] = feedback
                
                if formatted_sql:
                    tags.update({
                        "complexity": self._categorize_complexity(metrics),
                        "query_type": self._determine_query_type(formatted_sql)
                    })
                
                mlflow.set_tags(tags)
                
                # Log query details
                self._log_query_details(user_query, formatted_sql, error, latency)
                
        except Exception as e:
            print(f"Error logging to MLflow: {str(e)}")

    def _count_tables(self, sql: str) -> int:
        return sql.upper().count("FROM ") + sql.upper().count("JOIN ")

    def _count_joins(self, sql: str) -> int:
        return sql.upper().count("JOIN ")

    def _count_where_conditions(self, sql: str) -> int:
        return (sql.upper().count("WHERE ") + 
                sql.upper().count(" AND ") + 
                sql.upper().count(" OR "))

    def _categorize_performance(self, execution_time: float) -> str:
        """Categorize performance based on BigQuery execution time"""
        if execution_time < 0.5:  # Less than 500ms
            return "fast"
        elif execution_time < 2.0:  # Less than 2 seconds
            return "medium"
        return "slow"

    def _categorize_latency(self, latency: float) -> str:
        """Categorize latency"""
        if latency < 0.1:  # Less than 100ms
            return "low"
        elif latency < 0.5:  # Less than 500ms
            return "medium"
        return "high"

    def _categorize_complexity(self, metrics: Dict[str, float]) -> str:
        complexity_score = (
            metrics.get("table_count", 0) * 2 +
            metrics.get("join_count", 0) * 3 +
            metrics.get("where_conditions", 0)
        )
        
        if complexity_score < 5:
            return "simple"
        elif complexity_score < 10:
            return "moderate"
        return "complex"

    def _determine_query_type(self, sql: str) -> str:
        sql_upper = sql.upper()
        if "SELECT" in sql_upper:
            if "GROUP BY" in sql_upper:
                return "aggregate"
            elif "JOIN" in sql_upper:
                return "join"
            return "select"
        elif "INSERT" in sql_upper:
            return "insert"
        elif "UPDATE" in sql_upper:
            return "update"
        elif "DELETE" in sql_upper:
            return "delete"
        return "other"

    def _log_query_details(self, user_query: str, sql: str, error: Optional[str], latency: float) -> None:
        artifact_path = os.path.join(os.getcwd(), "query_details.txt")
        try:
            with open(artifact_path, "w") as f:
                f.write(f"User Query: {user_query}\n\n")
                f.write(f"Generated SQL:\n{sql}\n")
                f.write(f"Latency: {latency:.3f} seconds\n")
                if error:
                    f.write(f"\nError: {error}\n")
            
            mlflow.log_artifact(artifact_path)
        finally:
            if os.path.exists(artifact_path):
                os.remove(artifact_path)