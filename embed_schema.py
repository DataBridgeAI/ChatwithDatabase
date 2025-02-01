

# from sentence_transformers import SentenceTransformer
# from langchain_community.vectorstores import FAISS
# from langchain.embeddings.base import Embeddings
# import json
# import numpy as np

# class SentenceTransformerEmbedding(Embeddings):
#     def __init__(self, model_name: str):
#         self.model = SentenceTransformer(model_name)

#     def embed_documents(self, texts: list) -> np.ndarray:
#         """Embeds the list of documents (texts) into their respective embeddings."""
#         return self.model.encode(texts)

#     def embed_query(self, query: str) -> np.ndarray:
#         """Embeds a single query (string) into its respective embedding."""
#         return self.model.encode([query])

# def embed_and_store_schema():
#     """Embeds schema information and stores it in a FAISS index."""
#     with open("schema.json", "r") as f:
#         schema = json.load(f)

#     processed_schema = {}
#     for table_name, table_data in schema.items():
#         processed_schema[table_name] = []
#         for column_info in table_data:
#             processed_schema[table_name].append(column_info["name"]) 

#     texts = [f"Table: {table}, Columns: {', '.join(columns)}" for table, columns in processed_schema.items()]

#     # Use all-MiniLM-L6-v2 for embeddings
#     embedding = SentenceTransformerEmbedding('all-MiniLM-L6-v2')
#     embeddings = embedding.embed_documents(texts)

#     print('----------------------Embeddings---------------------')
#     print(embeddings)
#     print('----------------------Embeddings---------------------')
#     print('----------------------Text---------------------')
#     print(texts)
#     print('----------------------Text---------------------')

#     # Check if lengths match
#     if len(texts) != len(embeddings):
#         print("Error: Unequal number of texts and embeddings. Skipping FAISS index creation.")
#         return

#     # Create the FAISS index from the embeddings and texts
#     db = FAISS.from_texts(texts, embedding)
#     db.save_local("faiss_index")

# if __name__ == "__main__":
#     embed_and_store_schema()



from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
import json
import numpy as np

class SentenceTransformerEmbedding(Embeddings):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list) -> np.ndarray:
        """Embeds the list of documents (texts) into their respective embeddings."""
        return self.model.encode(texts)

    def embed_query(self, query: str) -> np.ndarray:
        """Embeds a single query (string) into its respective embedding."""
        return self.model.encode([query])

def embed_and_store_schema():
    """Embeds schema information and stores it in a FAISS index."""
    with open("schema.json", "r") as f:
        schema = json.load(f)

    processed_schema = {}
    for table_name, table_data in schema.items():
        processed_schema[table_name] = []
        for column_info in table_data:
            processed_schema[table_name].append(column_info["name"]) 

    texts = [f"Table: {table}, Columns: {', '.join(columns)}" for table, columns in processed_schema.items()]

    # Use all-MiniLM-L6-v2 for embeddings
    embedding = SentenceTransformerEmbedding('all-MiniLM-L6-v2')
    embeddings = embedding.embed_documents(texts)

    # Convert embeddings to np.float32 (FAISS requirement)
    embeddings = np.array(embeddings, dtype=np.float32)

    print('----------------------Embeddings---------------------')
    print(embeddings)
    print('----------------------Embeddings---------------------')
    print('----------------------Text---------------------')
    print(texts)
    print('----------------------Text---------------------')

    # Check if lengths match
    if len(texts) != len(embeddings):
        print("Error: Unequal number of texts and embeddings. Skipping FAISS index creation.")
        return

    # Check the shape of embeddings (should be (n, 384))
    print(f"Shape of embeddings: {embeddings.shape}")

    # Ensure the embeddings are 2D and have the correct shape
    if embeddings.ndim != 2 or embeddings.shape[1] != 384:
        print(f"Error: Embeddings have incorrect shape. Expected (n, 384), got {embeddings.shape}")
        return

    # Create the FAISS index from the embeddings and texts
    db = FAISS.from_texts(texts, embedding)
    
    # Verify the index dimensionality
    print(f"FAISS index dimensionality: {db.index.d}")
    
    # Save the FAISS index
    db.save_local("faiss_index")

if __name__ == "__main__":
    embed_and_store_schema()
