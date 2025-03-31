import json
from typing import Dict, List, Tuple
import re
from google.cloud import storage
from datetime import datetime

class PromptValidator:
    def __init__(self, project_id: str, bucket_name: str):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()
        self.bias_patterns = {
            'gender_bias': r'\b(male|female|men|women|gender)\b',
            'racial_bias': r'\b(race|ethnic|white|black|asian)\b',
            'age_bias': r'\b(young|old|age|elderly)\b'
        }
        
    def validate_sql_correctness(self, generated_sql: str) -> Tuple[bool, str]:
        """Validate basic SQL syntax and structure"""
        required_elements = {
            'select': r'SELECT\s+',
            'from': r'FROM\s+',
            'table_reference': r'\w+\.\w+\.\w+'
        }
        
        for element, pattern in required_elements.items():
            if not re.search(pattern, generated_sql, re.IGNORECASE):
                return False, f"Missing required SQL element: {element}"
        
        return True, "SQL validation passed"

    def check_for_bias(self, generated_sql: str) -> Dict[str, bool]:
        """Check for potential bias in generated SQL"""
        bias_results = {}
        for bias_type, pattern in self.bias_patterns.items():
            bias_results[bias_type] = bool(re.search(pattern, generated_sql, re.IGNORECASE))
        return bias_results

    def validate_prompt_template(self, prompt_template: str) -> Tuple[bool, List[str]]:
        """Validate prompt template structure and required elements"""
        required_elements = [
            "{schema}",
            "{project_id}",
            "{dataset_id}",
            "{user_query}"
        ]
        
        issues = []
        for element in required_elements:
            if element not in prompt_template:
                issues.append(f"Missing required element: {element}")
        
        return len(issues) == 0, issues

    def store_prompt_version(self, prompt_template: str, version_metadata: Dict) -> str:
        """Store a new version of the prompt template in GCS"""
        bucket = self.storage_client.bucket(self.bucket_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_id = f"v_{timestamp}"
        
        prompt_data = {
            "template": prompt_template,
            "version_id": version_id,
            "timestamp": timestamp,
            "metadata": version_metadata
        }
        
        blob = bucket.blob(f"prompts/{version_id}.json")
        blob.upload_from_string(json.dumps(prompt_data))
        
        return version_id

    def get_latest_prompt(self) -> Dict:
        """Retrieve the latest prompt template from GCS"""
        bucket = self.storage_client.bucket(self.bucket_name)
        blobs = list(bucket.list_blobs(prefix="prompts/"))
        if not blobs:
            raise ValueError("No prompt templates found in storage")
            
        latest_blob = max(blobs, key=lambda x: x.name)
        return json.loads(latest_blob.download_as_string())