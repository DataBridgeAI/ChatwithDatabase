import json
import sys
import logging
import os
from typing import Dict, List
from google.cloud import storage

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from ModelValidation.prompt_validator import PromptValidator
from ModelValidation.config import PROJECT_ID, PROMPT_BUCKET_NAME, EXPECTED_PROMPT_TEMPLATE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_initial_prompt() -> Dict:
    """Create the initial prompt template based on config"""
    return {
        "version": EXPECTED_PROMPT_TEMPLATE["version"],
        "template": EXPECTED_PROMPT_TEMPLATE["template"],
        "metadata": EXPECTED_PROMPT_TEMPLATE["metadata"]
    }

def validate_stored_prompts(validator: PromptValidator) -> Dict[str, List[str]]:
    """Validate all stored prompt templates in GCS"""
    validation_results = {}
    
    try:
        bucket = validator.storage_client.bucket(validator.bucket_name)
        blobs = bucket.list_blobs(prefix="prompts/")
        
        # Filter out directory entries and get only .json files
        blob_list = [b for b in blobs if b.name.endswith('.json')]
        
        if not blob_list:
            logger.warning(f"No prompt JSON files found in bucket '{validator.bucket_name}' with prefix 'prompts/'")
            # Create initial prompt if none exists
            logger.info("Creating initial prompt template...")
            initial_prompt = create_initial_prompt()
            version_id = validator.store_prompt_version(
                initial_prompt["template"],
                initial_prompt["metadata"]
            )
            logger.info(f"Created initial prompt with version_id: {version_id}")
            return validation_results
            
        for blob in blob_list:
            logger.info(f"Processing blob: {blob.name}")
            try:
                content = blob.download_as_string()
                prompt_data = json.loads(content)
                
                # Validate against expected structure
                required_keys = ["version", "template", "metadata"]
                missing_keys = [key for key in required_keys if key not in prompt_data]
                
                if missing_keys:
                    logger.warning(f"Prompt in {blob.name} missing required keys: {missing_keys}")
                    validation_results[blob.name] = [f"Missing required keys: {missing_keys}"]
                    continue
                
                # Validate metadata structure
                required_metadata = ["description", "author", "created_at"]
                missing_metadata = [key for key in required_metadata if key not in prompt_data["metadata"]]
                
                if missing_metadata:
                    logger.warning(f"Prompt metadata in {blob.name} missing required fields: {missing_metadata}")
                    validation_results[blob.name] = [f"Missing metadata fields: {missing_metadata}"]
                    continue
                
                # Validate template content
                is_valid, issues = validator.validate_prompt_template(prompt_data["template"])
                validation_results[blob.name] = issues if not is_valid else []
                
                if not is_valid:
                    logger.warning(f"Invalid prompt template found in {blob.name}")
                    logger.warning(f"Issues: {issues}")
                    
            except json.JSONDecodeError as je:
                logger.error(f"JSON parsing error in blob {blob.name}: {str(je)}")
                validation_results[blob.name] = [f"JSON parsing error: {str(je)}"]
                continue
            except Exception as e:
                logger.error(f"Error processing blob {blob.name}: {str(e)}")
                validation_results[blob.name] = [f"Processing error: {str(e)}"]
                continue
                
    except Exception as e:
        logger.error(f"Error accessing storage bucket: {str(e)}")
        raise
        
    return validation_results

def main():
    try:
        # Initialize GCP credentials if needed
        if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            logger.warning("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
            
        logger.info(f"Initializing validator with project_id={PROJECT_ID}, bucket={PROMPT_BUCKET_NAME}")
        validator = PromptValidator(
            project_id=PROJECT_ID,
            bucket_name=PROMPT_BUCKET_NAME
        )
        
        validation_results = validate_stored_prompts(validator)
        invalid_prompts = {k: v for k, v in validation_results.items() if v}
        
        if invalid_prompts:
            logger.error("Found invalid prompt templates:")
            print(json.dumps(invalid_prompts, indent=2))
            sys.exit(1)
        else:
            logger.info("All prompt templates are valid")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Prompt validation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()


