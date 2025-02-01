import numpy as np
from sentence_transformers import SentenceTransformer
# from langchain.embeddings import Embeddings
from langchain.embeddings.base import Embeddings

from langchain_community.vectorstores import FAISS

class SentenceTransformerEmbedding(Embeddings):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list) -> np.ndarray:
        """Embeds the list of documents (texts) into their respective embeddings."""
        return self.model.encode(texts)

    def embed_query(self, query: str) -> np.ndarray:
        """Embeds a single query (string) into its respective embedding."""
        return self.model.encode([query])

def retrieve_relevant_docs(query, schema):
    # Initialize embedding model
    embedding = SentenceTransformerEmbedding('all-MiniLM-L6-v2')
    
    # Generate embedding for the query
    query_embedding = embedding.embed_query(query)  # Get the query embedding
    
    # Print the shape of the query embedding for debugging
    print("Query embedding shape:", query_embedding.shape)

    
    # Ensure query_embedding is a numpy array with the correct shape and dtype
    query_embedding = np.array(query_embedding, dtype=np.float32)
    
    # Reshape the query embedding to (1, d) if it's a 1D array (for single query)
    if query_embedding.ndim == 1:
        query_embedding = query_embedding.reshape(1, -1)
    
    # Load the FAISS index
    db = FAISS.load_local("faiss_index", embedding, allow_dangerous_deserialization=True)
    
    # Perform the similarity search
    docs = db.similarity_search_by_vector(query_embedding, k=3)
    
    # Return the matching documents
    return "\n".join([doc.page_content for doc in docs])
