
import time
import sys, os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from ai.llm import clean_sql
from database.query_executor import execute_bigquery_query
from database.schema import get_bigquery_schema

# Define test parameters
project_id = "chatwithdata-451800"
dataset_id = "RetailDataset"
user_query = "List the top 5 customers by total purchase amount."
schema = get_bigquery_schema(project_id, dataset_id)

# Prompt template from llm.py
prompt_template = PromptTemplate(
    template="""Convert this English question into an accurate **BigQuery SQL query**.

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

Return **ONLY** the SQL query.""",
    input_variables=["schema", "user_query", "project_id", "dataset_id"]
)

results = []

param_configs = [
    {
        "temperature": 0.2,
        "top_p": 0.8,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.2,
        "top_p": 0.8,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.2,
        "top_p": 0.8,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.2,
        "top_p": 0.8,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.2,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.2,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.2,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.2,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.2,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.2,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.2,
        "top_p": 1.0,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.2,
        "top_p": 1.0,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.5,
        "top_p": 0.8,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.5,
        "top_p": 0.8,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.5,
        "top_p": 0.8,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.5,
        "top_p": 0.8,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.5,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.5,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.5,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.5,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.5,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.5,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.5,
        "top_p": 1.0,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.5,
        "top_p": 1.0,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.7,
        "top_p": 0.8,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.7,
        "top_p": 0.8,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.7,
        "top_p": 0.8,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.7,
        "top_p": 0.8,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.7,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.7,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.5
    },
    {
        "temperature": 0.7,
        "top_p": 1.0,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.0
    },
    {
        "temperature": 0.7,
        "top_p": 1.0,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5
    }
]

for config in param_configs:
    print(f"Testing config: {config}")
    llm = ChatOpenAI(
        model_name="gpt-4",
        temperature=config["temperature"],
        top_p=config["top_p"],
        frequency_penalty=config["frequency_penalty"],
        presence_penalty=config["presence_penalty"]
    )

    chain = LLMChain(llm=llm, prompt=prompt_template)
    try:
        sql = chain.run({
            "schema": schema,
            "user_query": user_query,
            "project_id": project_id,
            "dataset_id": dataset_id
        })
        sql = clean_sql(sql)
        df, exec_time = execute_bigquery_query(sql)
        score = 1 if "Error" not in df.columns else 0

        results.append({
            **config,
            "sql": sql,
            "success": score,
            "execution_time": exec_time
        })

    except Exception as e:
        results.append({
            **config,
            "sql": "Generation failed",
            "success": 0,
            "execution_time": 0,
            "error": str(e)
        })

# Save results
pd.DataFrame(results).to_csv("tuning_results.csv", index=False)
print("Tuning complete. Results saved to tuning_results.csv.")