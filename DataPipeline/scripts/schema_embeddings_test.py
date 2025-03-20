# import json
# import chromadb
# from google.cloud import bigquery
# import numpy as np
# from langchain_google_vertexai import VertexAIEmbeddings
# from sklearn.metrics.pairwise import cosine_similarity
# import os

# # Configuration Parameters
# PROJECT_ID = "chatwithdata-451800"
# DATASET_ID = "RetailDataset"
# VERTEX_MODEL = "textembedding-gecko@003"
# CHROMA_PATH = "/tmp/chromadb_store"

# # Initialize Vertex AI Embeddings
# embedding_model = VertexAIEmbeddings(model=VERTEX_MODEL)


# def extract_schema():
#     """Extract schema details with rich semantic descriptions."""
#     client = bigquery.Client(project=PROJECT_ID)
#     dataset_ref = client.dataset(DATASET_ID)
#     tables = client.list_tables(dataset_ref)

#     schema_data = []
#     for table in tables:
#         table_ref = dataset_ref.table(table.table_id)
#         table_obj = client.get_table(table_ref)
#         table_schema = table_obj.schema

#         # Get table description if available
#         table_desc = table_obj.description or table.table_id

#         for field in table_schema:
#             # Create a rich semantic description for each column
#             field_desc = field.description or ""
#             semantic_text = (
#                 f"This column represents {field.name} in the {table.table_id} table. "
#                 f"It stores {field_desc if field_desc else field.name} "
#                 f"with data type {field.field_type}. "
#                 f"The {table.table_id} table {table_desc}."
#             )
            
#             schema_data.append({
#                 "table": table.table_id,
#                 "column": field.name,
#                 "semantic_text": semantic_text
#             })
    
#     return schema_data

# def generate_schema_embeddings():
#     """Generate embeddings using rich semantic descriptions."""
#     schema_data = extract_schema()
#     # Use semantic text for embeddings instead of just table:column
#     schema_texts = [item['semantic_text'] for item in schema_data]
    
#     # Create embeddings for semantic descriptions
#     schema_embeddings = embedding_model.embed_documents(schema_texts)
    
#     # Create a dictionary of schema embeddings
#     schema_dict = {}
#     for idx, item in enumerate(schema_data):
#         key = f"{item['table']}:{item['column']}"
#         schema_dict[key] = {
#             'embedding': schema_embeddings[idx],
#             'semantic_text': item['semantic_text']
#         }
    
#     return schema_dict

# def generate_user_input_embedding(user_input):
#     """Generate embedding for user input"""
#     user_input_embedding = embedding_model.embed_documents([user_input])
#     return np.array(user_input_embedding[0])

# def process_user_input(user_input):
#     """Process user input and find relevant schema matches"""
#     try:
#         schema_embeddings = generate_schema_embeddings()
#         return find_top_matches(user_input, schema_embeddings)
#     except Exception as e:
#         print(f"Error processing user input: {str(e)}")
#         return []


# def find_top_matches(user_input, schema_embeddings, top_n=5, threshold=0.75):
#     """Find top matching schema based on semantic similarity."""
#     user_input_embedding = generate_user_input_embedding(user_input)
#     similarities = {}
    
#     for schema_key, schema_data in schema_embeddings.items():
#         schema_embedding = np.array(schema_data['embedding']).reshape(1, -1)
#         user_embedding = np.array(user_input_embedding).reshape(1, -1)
        
#         # Calculate cosine similarity
#         similarity = cosine_similarity(user_embedding, schema_embedding)[0][0]
#         similarities[schema_key] = {
#             'score': similarity,
#             'semantic_text': schema_data['semantic_text']
#         }
    
#     # Sort by similarity score and filter based on threshold
#     sorted_matches = sorted(
#         [(k, v) for k, v in similarities.items() if v['score'] >= threshold],
#         key=lambda x: x[1]['score'],
#         reverse=True
#     )
    
#     if not sorted_matches:
#         print("\n❌ No relevant schema found for this query.")
#         print("The query appears to be unrelated to the database schema.")
#         return []
    
#     print(f"\nTop {min(top_n, len(sorted_matches))} matching table-column pairs for user input '{user_input}':")
#     for idx, (schema_key, data) in enumerate(sorted_matches[:top_n], 1):
#         print(f"{idx}. {schema_key}")
#         print(f"   Score: {data['score']:.2f}")
#         print(f"   Context: {data['semantic_text']}\n")
    
#     return sorted_matches[:top_n]

# # Example usage with a while loop for user input
# if __name__ == "__main__":
#     while True:
#         user_input = input("\nEnter a query (or type 'exit' to quit): ")
        
#         if user_input.lower() == "exit":
#             print("Exiting the program.")
#             break
        
#         top_matches = process_user_input(user_input)



import json
import chromadb
from google.cloud import bigquery
import numpy as np
from langchain_google_vertexai import VertexAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import os

# Configuration Parameters
PROJECT_ID = "chatwithdata-451800"
DATASET_ID = "RetailDataset"
VERTEX_MODEL = "textembedding-gecko@003"
CHROMA_PATH = "/tmp/chromadb_store"

# Initialize Vertex AI Embeddings
embedding_model = VertexAIEmbeddings(model=VERTEX_MODEL)

def extract_schema():
    """Extract schema details with rich semantic descriptions."""
    client = bigquery.Client(project=PROJECT_ID)
    dataset_ref = client.dataset(DATASET_ID)
    tables = client.list_tables(dataset_ref)

    schema_data = []
    for table in tables:
        table_ref = dataset_ref.table(table.table_id)
        table_obj = client.get_table(table_ref)
        table_schema = table_obj.schema

        # Get table description if available
        table_desc = table_obj.description or table.table_id

        for field in table_schema:
            # Create a rich semantic description for each column
            field_desc = field.description or ""
            semantic_text = (
                f"This column represents {field.name} in the {table.table_id} table. "
                f"It stores {field_desc if field_desc else field.name} "
                f"with data type {field.field_type}. "
                f"The {table.table_id} table {table_desc}."
            )
            
            schema_data.append({
                "table": table.table_id,
                "column": field.name,
                "semantic_text": semantic_text
            })
    
    return schema_data

def generate_schema_embeddings():
    """Generate embeddings using rich semantic descriptions."""
    schema_data = extract_schema()
    # Use semantic text for embeddings instead of just table:column
    schema_texts = [item['semantic_text'] for item in schema_data]
    
    # Create embeddings for semantic descriptions
    schema_embeddings = embedding_model.embed_documents(schema_texts)
    
    # Create a dictionary of schema embeddings
    schema_dict = {}
    for idx, item in enumerate(schema_data):
        key = f"{item['table']}:{item['column']}"
        schema_dict[key] = {
            'embedding': schema_embeddings[idx],
            'semantic_text': item['semantic_text']
        }
    
    return schema_dict

def generate_user_input_embedding(user_input):
    """Generate embedding for user input."""
    user_input_embedding = embedding_model.embed_documents([user_input])
    return np.array(user_input_embedding[0])

def process_user_input(user_input):
    """Process user input and find relevant schema matches."""
    try:
        schema_embeddings = generate_schema_embeddings()
        return find_top_matches(user_input, schema_embeddings)
    except Exception as e:
        print(f"Error processing user input: {str(e)}")
        return []

def find_top_matches(user_input, schema_embeddings, top_n=5, threshold=0.75):
    """Find top matching schema based on semantic similarity."""
    user_input_embedding = generate_user_input_embedding(user_input)
    similarities = {}
    
    for schema_key, schema_data in schema_embeddings.items():
        schema_embedding = np.array(schema_data['embedding']).reshape(1, -1)
        user_embedding = np.array(user_input_embedding).reshape(1, -1)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(user_embedding, schema_embedding)[0][0]
        similarities[schema_key] = {
            'score': similarity,
            'semantic_text': schema_data['semantic_text']
        }
    
    # Sort by similarity score and filter based on threshold
    sorted_matches = sorted(
        [(k, v) for k, v in similarities.items() if v['score'] >= threshold],
        key=lambda x: x[1]['score'],
        reverse=True
    )
    
    if not sorted_matches:
        print("\n❌ No relevant schema found for this query.")
        print("The query appears to be unrelated to the database schema.")
        return []
    
    print(f"\nTop {min(top_n, len(sorted_matches))} matching table-column pairs for user input '{user_input}':")
    for idx, (schema_key, data) in enumerate(sorted_matches[:top_n], 1):
        print(f"{idx}. {schema_key}")
        print(f"   Score: {data['score']:.2f}")
        print(f"   Context: {data['semantic_text']}\n")
    
    return sorted_matches[:top_n]

# Example usage with a while loop for user input
if __name__ == "__main__":
    while True:
        user_input = input("\nEnter a query (or type 'exit' to quit): ")
        
        if user_input.lower() == "exit":
            print("Exiting the program.")
            break
        
        top_matches = process_user_input(user_input)
