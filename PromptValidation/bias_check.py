import logging
from typing import List, Dict
import json
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from PromptValidation.prompt_validator import PromptValidator
from PromptValidation.test_queries import TEST_QUERIES
from PromptValidation.config import PROJECT_ID, DATASET_ID, PROMPT_BUCKET_NAME, RETAIL_SCHEMA
from src.ai.llm import generate_sql, load_prompt_template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_bias_in_queries(queries: List[str], validator: PromptValidator) -> Dict[str, List[str]]:
    """Check for bias in a list of test queries and their generated SQL"""
    # Ensure prompt template is loaded
    load_prompt_template(PROMPT_BUCKET_NAME)
    
    biased_queries = {
        'gender_bias': [],
        'racial_bias': [],
        'age_bias': []
    }
    
    for query in queries:
        try:
            generated_sql = generate_sql(
                user_query=query,
                schema=RETAIL_SCHEMA,
                project_id=PROJECT_ID,
                dataset_id=DATASET_ID
            )
            
            bias_results = validator.check_for_bias(generated_sql)
            
            for bias_type, has_bias in bias_results.items():
                if has_bias:
                    biased_queries[bias_type].append(query)
                    logger.warning(f"Bias detected - Type: {bias_type}, Query: {query}")
                    
        except Exception as e:
            logger.error(f"Error processing query '{query}': {str(e)}")
    
    return biased_queries

def main():
    try:
        validator = PromptValidator(
            project_id=PROJECT_ID,
            bucket_name=PROMPT_BUCKET_NAME
        )
        
        bias_results = check_bias_in_queries(TEST_QUERIES, validator)
        total_biased = sum(len(queries) for queries in bias_results.values())
        
        if total_biased > 0:
            logger.error(f"Found {total_biased} queries with potential bias")
            print(json.dumps(bias_results, indent=2))
            sys.exit(1)
        else:
            logger.info("No bias detected in test queries")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Bias check failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()






