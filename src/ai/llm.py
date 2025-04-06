from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize LLM with None, will be set later if not available now
llm = None

# Try to initialize LLM if API key is available
if openai_api_key:
    try:
        llm = ChatOpenAI(model_name="gpt-4", temperature=0.3, openai_api_key=openai_api_key)
        print("LLM initialized with API key from environment")
    except Exception as e:
        print(f"Failed to initialize LLM: {str(e)}")

def set_openai_api_key(api_key):
    """Set the OpenAI API key and reinitialize the LLM."""
    global llm, openai_api_key
    openai_api_key = api_key
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.3, openai_api_key=api_key)
    return True

# Default prompt template
PROMPT_TEMPLATE = """
You are an expert SQL query generator for BigQuery. Your task is to convert natural language questions into SQL queries.

Schema information:
{schema}

User query: {user_query}

Project ID: {project_id}
Dataset ID: {dataset_id}

Generate a SQL query that answers the user's question. The query should be valid BigQuery SQL.
Only return the SQL query without any explanations.
"""

def load_prompt_template() -> None:
    """Initialize the prompt template."""
    global PROMPT_TEMPLATE
    # The template is already loaded as a constant
    print("Using default prompt template")

def clean_sql(raw_sql: str) -> str:
    """Remove unnecessary markdown and whitespace from SQL."""
    cleaned_sql = raw_sql.replace("sql", "").replace("```", "").strip()
    return "\n".join(line.strip() for line in cleaned_sql.splitlines() if line.strip())

def generate_sql(user_query: str, schema: str, project_id: str, dataset_id: str) -> str:
    """Generate SQL query from natural language using GPT-4 for BigQuery."""
    global PROMPT_TEMPLATE, llm, openai_api_key

    # Check if LLM is initialized
    if not llm:
        if not openai_api_key:
            raise ValueError("OpenAI API key is not set. Please set it using the credentials endpoint.")
        llm = ChatOpenAI(model_name="gpt-4", temperature=0.3, openai_api_key=openai_api_key)

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
