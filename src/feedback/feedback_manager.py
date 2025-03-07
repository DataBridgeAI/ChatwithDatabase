import time
import uuid
import chromadb


chroma_client = chromadb.PersistentClient(path="./feedback_db")


def store_feedback(user_query, generated_sql, feedback, 
                   execution_success=None, execution_time=None):
    """Store feedback in ChromaDB."""
    try:
        doc_id = str(uuid.uuid4())
        metadata = {
            "user_query": user_query,
            "generated_sql": generated_sql,
            "feedback": feedback if feedback is not None else "None",
            "execution_success": str(execution_success) if execution_success is not None else "None",
            "execution_time": str(execution_time) if execution_time is not None else "None",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        return True
    except Exception:
        return False


def get_relevant_feedback(user_query):
    """Retrieve relevant positive feedback examples from ChromaDB using RAG."""
    try:
        feedback_collection = chroma_client.get_or_create_collection(name="query_feedback")

        results = feedback_collection.query(
            query_texts=[user_query],
            where={"feedback": "positive"},
            n_results=3
        )

        examples = []
        for i, metadata in enumerate(results["metadatas"][0]):
            example = (
                f"Example {i+1}:
"
                f"Query: {metadata['user_query']}
"
                f"SQL: {metadata['generated_sql']}
"
            )
            examples.append(example)

        return "\n".join(examples) if examples else "No relevant positive feedback examples found."
    except Exception:
        return "No relevant positive feedback examples found due to an error."