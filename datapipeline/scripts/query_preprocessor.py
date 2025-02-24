from google.cloud import bigquery, storage
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import re
from detoxify import Detoxify

# Google Cloud configurations
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "Songs"
BUCKET_NAME = "schema-embeddings-db"

# Initialize clients
bq_client = bigquery.Client(project=PROJECT_ID)
storage_client = storage.Client()

# Load embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Load LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)

def check_toxicity(query: str) -> bool:
    """Checks if the user query contains toxic or harmful content."""
    toxicity_score = Detoxify('original').predict(query)
    return toxicity_score['toxicity'] < 0.5  # Threshold for safety

def download_from_gcs():
    """Downloads schema embeddings from GCS."""
    bucket = storage_client.bucket(BUCKET_NAME)

    for gcs_path, local_path in [("schema/schema_texts.pkl", "schema_texts.pkl"), 
                                 ("schema/schema_index.faiss", "schema_index.faiss")]:
        blob = bucket.blob(gcs_path)
        blob.download_to_filename(local_path)

def load_schema_embeddings():
    """Loads schema embeddings from local files."""
    download_from_gcs()
    with open("schema_texts.pkl", "rb") as f:
        schema_texts = pickle.load(f)
    with open("schema_index.faiss", "rb") as f:
        index = pickle.load(f)
    return index, schema_texts

def retrieve_relevant_schema(user_query):
    """Finds relevant schema details for a given user query."""
    index, schema_texts = load_schema_embeddings()
    query_embedding = embedding_model.encode([user_query], convert_to_numpy=True)
    _, indices = index.search(query_embedding, k=3)
    return "\n".join([schema_texts[i] for i in indices[0]])

def generate_sql(user_query, relevant_schema):
    """Generates an SQL query based on schema using an LLM."""
    prompt_template = PromptTemplate(
        template="""
        Convert the following English query to BigQuery SQL based on the given schema:
        
        Schema:
        {schema}
        
        Query: "{user_query}"
        """,
        input_variables=["schema", "user_query"]
    )
    chain = LLMChain(llm=llm, prompt=prompt_template)
    return chain.run({"schema": relevant_schema, "user_query": user_query}).strip()

def execute_query(query):
    """Executes an SQL query in BigQuery."""
    df = bq_client.query(query).to_dataframe()
    return df

def retrieve_schema(user_query):
    """Processes a user query end-to-end."""
    relevant_schema = retrieve_relevant_schema(user_query)
    # sql_query = generate_sql(user_query, relevant_schema)
    # results = execute_query(sql_query)
    # print(results)

if __name__ == "__main__":
    user_query = "Show the total sales amount for each product in January 2024"
    retrieve_schema(user_query)
