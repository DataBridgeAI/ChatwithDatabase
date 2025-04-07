from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from google.cloud import storage
import json

# Initializing LLM i.e GPT 4 for this project
llm = ChatOpenAI(model_name="gpt-4", temperature=0.3)

# Global variable to store the prompt template
PROMPT_TEMPLATE = None

def load_prompt_template(bucket_name: str = "sql-prompts-store") -> None:
    """Load the latest prompt template from GCS bucket during app initialization."""
    global PROMPT_TEMPLATE
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix="prompts/"))
    
    if not blobs:
        raise ValueError("No prompt templates found in storage")
        
    latest_blob = max(blobs, key=lambda x: x.name)
    prompt_data = json.loads(latest_blob.download_as_string())
    PROMPT_TEMPLATE = prompt_data["template"]

def clean_sql(raw_sql: str) -> str:
    """Remove unnecessary markdown and whitespace from SQL."""
    cleaned_sql = raw_sql.replace("sql", "").replace("```", "").strip()
    return "\n".join(line.strip() for line in cleaned_sql.splitlines() if line.strip())

def generate_sql(user_query: str, schema: str, project_id: str, dataset_id: str) -> str:
    """Generate SQL query from natural language using GPT-4 for BigQuery."""
    global PROMPT_TEMPLATE
    
    if PROMPT_TEMPLATE is None:
        raise RuntimeError("Prompt template not loaded. Call load_prompt_template() during app initialization.")
    
    # Generate SQL using the template
    chain = LLMChain(llm=llm, prompt=PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["schema", "user_query", "project_id", "dataset_id"]
    ))
    
    response = chain.run({
        "schema": schema,
        "user_query": user_query,
        "project_id": project_id,
        "dataset_id": dataset_id
    })
    
    return clean_sql(response)
