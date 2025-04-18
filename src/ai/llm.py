from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from google.cloud import storage
import json
import os
import logging
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [LLM] %(message)s'
)
logger = logging.getLogger(__name__)

# Function to set OpenAI API key that's missing
def set_openai_api_key(api_key: str) -> None:
    """Set the OpenAI API key for the application."""
    logger.info("Setting new OpenAI API key")
    os.environ["OPENAI_API_KEY"] = api_key
    # Reinitialize the LLM with the new key
    global llm
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.3)
    logger.info("LLM reinitialized with new API key")


# Initializing LLM i.e GPT 4 for this project
llm = ChatOpenAI(model_name="gpt-4", temperature=0.3)
logger.info("Initialized LLM with model: gpt-4")

# Global variable to store the prompt template
PROMPT_TEMPLATE = None

def load_prompt_template(bucket_name: str = "sql-prompts-store") -> None:
    """Load the latest prompt template from GCS bucket during app initialization."""
    global PROMPT_TEMPLATE
    logger.info(f"Loading prompt template from bucket: {bucket_name}")
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix="prompts/"))
    
    if not blobs:
        logger.error("No prompt templates found in storage")
        raise ValueError("No prompt templates found in storage")
        
    latest_blob = max(blobs, key=lambda x: x.name)
    logger.info(f"Found latest prompt template: {latest_blob.name}")
    prompt_data = json.loads(latest_blob.download_as_string())
    PROMPT_TEMPLATE = prompt_data["template"]
    logger.info("Successfully loaded prompt template")

def clean_sql(raw_sql: str) -> str:
    """Remove unnecessary markdown and whitespace from SQL."""
    cleaned_sql = raw_sql.replace("sql", "").replace("```", "").strip()
    return "\n".join(line.strip() for line in cleaned_sql.splitlines() if line.strip())

def generate_sql(user_query: str, schema: str, project_id: str, dataset_id: str) -> str:
    """Generate SQL query from natural language using GPT-4 for BigQuery."""
    global PROMPT_TEMPLATE
    
    if PROMPT_TEMPLATE is None:
        logger.error("Prompt template not loaded")
        raise RuntimeError("Prompt template not loaded. Call load_prompt_template() during app initialization.")
    
    logger.info(f"Generating SQL for query: {user_query}")
    logger.debug(f"Using project_id: {project_id}, dataset_id: {dataset_id}")
    
    # Create the prompt template
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["schema", "user_query", "project_id", "dataset_id"]
    )
    
    chain = prompt | llm
    response = chain.invoke({
        "schema": schema,
        "user_query": user_query,
        "project_id": project_id,
        "dataset_id": dataset_id
    })
    
    # Extract the content from the response
    if hasattr(response, 'content'):
        result = response.content
    else:
        result = str(response)
    
    logger.info(f"Generated SQL query: {result}")
    
    # Check if the response looks like SQL
    if not any(keyword in result.upper() for keyword in ['SELECT', 'WITH', 'CREATE']):
        raise ValueError(f"❌ Unable to generate SQL: {result}")
    
    cleaned_result = clean_sql(result.split("```sql")[-1] if "```sql" in result else result)
    logger.info(f"Cleaned SQL query: {cleaned_result}")
    
    return cleaned_result
