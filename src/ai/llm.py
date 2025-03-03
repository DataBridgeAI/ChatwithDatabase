from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

# Initialize LLM
llm = ChatOpenAI(model_name="gpt-4", temperature=0.3)

def clean_sql(raw_sql):
    """Remove unnecessary markdown and whitespace from SQL"""
    cleaned_sql = raw_sql.replace("sql", "").replace("```", "").strip()
    return "\n".join(line.strip() for line in cleaned_sql.splitlines() if line.strip())

def generate_sql(user_query, schema, project_id, dataset_id):
    """Generate SQL query from natural language using LLM for BigQuery."""
    
    prompt_template = PromptTemplate(
        template="""
        Convert this English question into an accurate **BigQuery SQL query**.

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

        Return **ONLY** the SQL query.
        """,
        input_variables=["schema", "user_query", "project_id", "dataset_id"]
    )

    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.run({
        "schema": schema,
        "user_query": user_query,
        "project_id": project_id,
        "dataset_id": dataset_id
    })
    
    return clean_sql(response)
