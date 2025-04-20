from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
from google.cloud import storage, bigquery
from collections import defaultdict
import logging
from .prompt_validator import PromptValidator
from .config import PROJECT_ID, DATASET_ID, PROMPT_BUCKET_NAME, EXPECTED_PROMPT_TEMPLATE, RETAIL_SCHEMA

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class PromptLearning:
    def __init__(self):
        logger.info("Initializing PromptLearning")
        self.validator = PromptValidator(PROJECT_ID, PROMPT_BUCKET_NAME)
        self.storage_client = storage.Client()
        self.bucket_name = PROMPT_BUCKET_NAME
        self.current_prompt = None
        self.current_version = None
        self.max_rules = 10
        self.performance_threshold = 0.8
        self.min_feedback_confidence = 0.7
        logger.info(f"PromptLearning initialized with bucket: {self.bucket_name}, max_rules: {self.max_rules}")

    def analyze_feedback(self, time_window_hours: int = 24) -> Dict:
        """Analyze recent feedback to identify patterns"""
        logger.info(f"Starting feedback analysis for past {time_window_hours} hours")
        
        query = """
        SELECT 
            user_question,
            generated_sql,
            feedback,
            execution_success,
            query_type,
            TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), timestamp, SECOND) as time_since_feedback
        FROM `{}.Feedback_Dataset.user_feedback`
        WHERE TIMESTAMP_ADD(timestamp, INTERVAL @hours HOUR) >= CURRENT_TIMESTAMP()
        """.format(PROJECT_ID)
        
        logger.debug(f"Executing BigQuery feedback analysis query:\n{query}")
        client = bigquery.Client()
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("hours", "INT64", time_window_hours)
            ]
        )
        
        try:
            query_job = client.query(query, job_config=job_config)
            results = query_job.result()
            logger.info(f"Query completed. Job ID: {query_job.job_id}")
        except Exception as e:
            logger.error(f"Failed to execute BigQuery query: {str(e)}")
            raise
        
        patterns = defaultdict(int)
        total_queries = 0
        failed_queries = []
        query_type_stats = defaultdict(lambda: {"total": 0, "failed": 0})
        
        logger.info("Processing feedback results")
        for row in results:
            total_queries += 1
            query_type_stats[row.query_type]["total"] += 1
            
            if row.feedback == "0":  # Negative feedback
                logger.debug(f"Processing negative feedback for query type: {row.query_type}")
                query_info = {
                    "question": row.user_question,
                    "sql": row.generated_sql,
                    "execution_success": row.execution_success,
                    "query_type": row.query_type,
                    "time_since_feedback": row.time_since_feedback
                }
                
                failed_queries.append(query_info)
                query_type_stats[row.query_type]["failed"] += 1
                patterns[row.query_type] += 1
                logger.debug(f"Failed query details:\n{json.dumps(query_info, indent=2)}")

        # Log query type statistics
        logger.info("Query type statistics:")
        for qtype, stats in query_type_stats.items():
            logger.info(f"  {qtype}: Total={stats['total']}, Failed={stats['failed']}")
        
        analysis_results = {
            "total_queries": total_queries,
            "failed_queries": failed_queries,
            "failure_patterns": dict(patterns),
            "query_type_stats": dict(query_type_stats),
            "success_rate": 1 - (len(failed_queries) / total_queries) if total_queries > 0 else 1
        }
        
        logger.info(f"Feedback analysis complete. Total queries: {total_queries}, Failed: {len(failed_queries)}")
        logger.info(f"Success rate: {analysis_results['success_rate']:.2%}")
        logger.debug(f"Failure patterns: {dict(patterns)}")
        
        return analysis_results

    def should_update_prompt(self, feedback_analysis: Dict) -> Tuple[bool, str]:
        """
        Determine if prompt should be updated based on feedback analysis.
        
        Returns:
            Tuple[bool, str]: (should_update, reason)
        """
        if feedback_analysis["feedback_confidence"] < self.min_feedback_confidence:
            return False, "Low confidence in feedback analysis"
            
        if feedback_analysis["success_rate"] < self.performance_threshold:
            # Check if there are clear patterns in failures
            if feedback_analysis["failure_patterns"]:
                most_common_issue = max(feedback_analysis["failure_patterns"].items(), key=lambda x: x[1])
                return True, f"Low success rate with clear pattern: {most_common_issue[0]}"
            return True, "Low success rate across queries"
            
        return False, "Current performance meets threshold"

    def generate_new_rules(self, failed_queries: List[Dict]) -> List[str]:
        """Generate new rules based on failed queries"""
        logger.info(f"Generating new rules from {len(failed_queries)} failed queries")
        from langchain_openai import ChatOpenAI
        
        rules = []
        failure_groups = defaultdict(list)
        
        logger.debug("Grouping failed queries by failure type")
        for query in failed_queries:
            failure_groups[query["query_type"]].append(query)
        
        logger.info(f"Found {len(failure_groups)} distinct failure types")
        
        for query_type, queries in failure_groups.items():
            logger.debug(f"Generating rule for query type: {query_type}")
            sample_queries = queries[:3]
            
            prompt = f"""
            Analyze these failed SQL generations for query type: {query_type}
            
            Examples:
            {json.dumps(sample_queries, indent=2)}
            
            Schema Tables: {list(RETAIL_SCHEMA.keys())}
            
            Suggest a single, specific rule to improve SQL generation.
            Response format: Just the rule, no explanation.
            """
            
            try:
                llm = ChatOpenAI(model_name="gpt-4", temperature=0.2)
                rule = llm.predict(prompt).strip()
                logger.debug(f"Generated rule: {rule}")
                rules.append(rule)
                logger.info(f"Added new rule for {query_type}")
            except Exception as e:
                logger.error(f"Error generating rule for {query_type}: {str(e)}")
        
        final_rules = rules[:self.max_rules]
        logger.info(f"Generated {len(final_rules)} new rules")
        return final_rules

    def update_prompt_template(self, new_rules: List[str]) -> Tuple[str, str]:
        """Update prompt template with new rules"""
        logger.info("Starting prompt template update")
        current_template = EXPECTED_PROMPT_TEMPLATE["template"]
        prompt_parts = current_template.split("Rules:")
        base_prompt = prompt_parts[0].strip()
        
        logger.debug("Processing core rules")
        core_rules = [
            "1. Use exact column and table names as in the schema.",
            "2. Always include `{project_id}.{dataset_id}.table_name` format in FROM clauses.",
            "3. Do NOT use `sql` or markdown formatting in the output.",
            "4. Ensure SQL is formatted for Google BigQuery.",
            "5. If aggregating data, use `GROUP BY` correctly."
        ]
        
        existing_rules = []
        if len(prompt_parts) > 1:
            logger.debug("Extracting existing non-core rules")
            all_rules = [r.strip() for r in prompt_parts[1].split("\n") if r.strip()]
            existing_rules = [r for r in all_rules if not any(core_rule in r for core_rule in core_rules)]
        
        all_rules = (
            core_rules +
            [f"{i+6}. {rule}" for i, rule in enumerate(new_rules)]
        )
        
        final_rules = all_rules[:self.max_rules]
        logger.info(f"Combined {len(final_rules)} rules in total")
        
        new_template = f"{base_prompt}\n\nRules:\n" + "\n".join(final_rules)
        
        logger.debug("Validating new template")
        is_valid, issues = self.validator.validate_prompt_template(new_template)
        if not is_valid:
            logger.error(f"Template validation failed: {issues}")
            raise ValueError(f"Invalid prompt template: {issues}")
        
        version_id = self._store_new_version(new_template, new_rules)
        logger.info(f"New template stored with version: {version_id}")
        
        return new_template, version_id

    def _store_new_version(self, template: str, new_rules: List[str]) -> str:
        """Store new prompt version in GCS"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version_id = f"v_{timestamp}"
        logger.info(f"Storing new prompt version: {version_id}")
        
        prompt_data = {
            "version": EXPECTED_PROMPT_TEMPLATE["version"],
            "template": template,
            "version_id": version_id,
            "timestamp": timestamp,
            "metadata": {
                "description": "Updated prompt template",
                "author": "PromptLearning",
                "created_at": datetime.now().isoformat(),
                "new_rules": new_rules,
                "previous_version": self.current_version
            }
        }
        
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            blob = bucket.blob(f"prompts/{version_id}.json")
            blob.upload_from_string(json.dumps(prompt_data))
            logger.info(f"Successfully stored new version {version_id} in GCS")
        except Exception as e:
            logger.error(f"Failed to store new version in GCS: {str(e)}")
            raise
        
        return version_id







