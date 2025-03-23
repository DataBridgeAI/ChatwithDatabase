from typing import Dict, List
import mlflow
from datetime import datetime
from .prompt_validator import PromptValidator

class PromptMonitor:
    def __init__(self, validator: PromptValidator):
        self.validator = validator
        
    def log_prompt_metrics(self, 
                          prompt_version: str,
                          generated_sql: str,
                          execution_time: float,
                          bias_results: Dict[str, bool],
                          validation_results: Dict[str, str]) -> None:
        """Log prompt performance metrics to MLflow"""
        with mlflow.start_run(run_name=f"prompt_validation_{prompt_version}"):
            # Log metrics
            mlflow.log_metrics({
                "execution_time": execution_time,
                "sql_length": len(generated_sql),
                "bias_detected": any(bias_results.values())
            })
            
            # Log parameters
            mlflow.log_params({
                "prompt_version": prompt_version,
                "timestamp": datetime.now().isoformat()
            })
            
            # Log bias results
            for bias_type, detected in bias_results.items():
                mlflow.log_metric(f"bias_{bias_type}", int(detected))
            
            # Log validation results
            mlflow.log_dict(validation_results, "validation_results.json")

    def should_update_prompt(self, 
                           bias_results: Dict[str, bool],
                           validation_results: Dict[str, str],
                           threshold: float = 0.8) -> bool:
        """Determine if prompt needs updating based on monitoring results"""
        if any(bias_results.values()):
            return True
            
        validation_success = all(result == "passed" for result in validation_results.values())
        return not validation_success