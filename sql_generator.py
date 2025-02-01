from transformers import pipeline

llm = pipeline("text2text-generation", model="google/flan-t5-large")

def generate_sql(user_query, relevant_docs):
    prompt = f"""
    You are an expert in SQL for BigQuery.
    Schema Details: {relevant_docs}
    
    Convert the user question into an optimized SQL query.
    
    User Query: "{user_query}"
    SQL:
    """
    
    response = llm(prompt)
    return [resp["generated_text"] for resp in response]
