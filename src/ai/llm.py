from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from google.cloud import storage
import json
import logging
import sys

# Configure logging with console handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG to see all logs

# Create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add console handler to logger
logger.addHandler(console_handler)

# Prevent log propagation to avoid duplicate logs
logger.propagate = False

# Initializing LLM i.e GPT 4 for this project
llm = ChatOpenAI(model_name="gpt-4", temperature=0.3)

PROMPT_BUCKET_NAME = "sql-prompts-store"

def get_latest_prompt() -> dict:
    """Retrieve the latest prompt template from GCS"""
    logger.info("Fetching latest prompt template from GCS")
    storage_client = storage.Client()
    bucket = storage_client.bucket(PROMPT_BUCKET_NAME)
    blobs = list(bucket.list_blobs(prefix="prompts/"))
    if not blobs:
        logger.warning("No prompt templates found in GCS, using default template")
        default_template = {
            "template": """Convert this English question into an accurate **BigQuery SQL query**.

            **BigQuery Schema:**
            {schema}

            **Dataset:** `{project_id}.{dataset_id}`

            **User Query:** "{user_query}"

            **Rules:**
            1. Use exact column and table names as in the schema.
            2. Always include `{project_id}.{dataset_id}.table_name` format in FROM clauses.
            3. Do NOT use `sql` or markdown formatting in the output.
            4. Ensure SQL is formatted for Google BigQuery.
            5. If aggregating data, use `GROUP BY` correctly.

            Return **ONLY** the SQL query."""
        }
        logger.debug(f"Default template: {default_template}")
        return default_template
    
    latest_blob = max(blobs, key=lambda x: x.name)
    template_data = json.loads(latest_blob.download_as_string())
    logger.info(f"Retrieved template version: {template_data.get('version_id', 'unknown')}")
    logger.debug(f"Template content: {template_data}")
    return template_data

def clean_sql(raw_sql: str) -> str:
    """Remove unnecessary markdown and whitespace from SQL."""
    cleaned_sql = raw_sql.replace("sql", "").replace("```", "").strip()
    return "\n".join(line.strip() for line in cleaned_sql.splitlines() if line.strip())

def generate_sql(user_query: str, schema: str, project_id: str, dataset_id: str, prompt_template: str) -> str:
    """Generate SQL query from natural language using GPT-4 for BigQuery."""
    logger.info(f"Generating SQL for query: {user_query}")
    logger.debug(f"Using prompt template: {prompt_template}")
    
    # Generate SQL using the template
    chain = LLMChain(llm=llm, prompt=PromptTemplate(
        template=prompt_template,
        input_variables=["schema", "user_query", "project_id", "dataset_id"]
    ))
    
    response = chain.run({
        "schema": schema,
        "user_query": user_query,
        "project_id": project_id,
        "dataset_id": dataset_id
    })
    
    return clean_sql(response)
