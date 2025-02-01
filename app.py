# from flask import Flask, request, jsonify
# from google.cloud import bigquery
# from transformers import pipeline
# from schema import get_bigquery_schema
# from rag_retriever import retrieve_relevant_docs
# from sql_generator import generate_sql
# from sql_validator import validate_and_rank_sql
# from feedback_manager import log_feedback
# import json

# app = Flask(__name__)
# bq_client = bigquery.Client()
# llm = pipeline("text2text-generation", model="google/flan-t5-large")

# @app.route("/", methods=["GET"])
# def home():
#     return jsonify({"message": "Chat with Database API is running!"})

# @app.route("/query", methods=["POST"])
# def query():
#     user_input = request.json["query"]
#     schema = get_bigquery_schema()

#     # Retrieve relevant schema and past queries using RAG
#     relevant_docs = retrieve_relevant_docs(user_input, schema)

#     # Generate SQL using structured prompting
#     sql_candidates = generate_sql(user_input, relevant_docs)

#     # Validate and rank SQL queries
#     best_sql = validate_and_rank_sql(sql_candidates)

#     if not best_sql:
#         return jsonify({"error": "Failed to generate a valid SQL query"}), 400

#     # Execute SQL in BigQuery
#     query_job = bq_client.query(best_sql)
#     results = query_job.result()
#     data = [dict(row) for row in results]

#     response = {
#         "query": best_sql,
#         "results": data,
#         "explanation": f"The query was generated based on similar past queries and schema details."
#     }

#     return jsonify(response)

# @app.route("/feedback", methods=["POST"])
# def feedback():
#     feedback_data = request.json
#     log_feedback(feedback_data)
#     return jsonify({"message": "Feedback recorded, model will improve."})

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8080)
from flask import Flask, request, jsonify, render_template
from google.cloud import bigquery
from transformers import pipeline
from schema import get_bigquery_schema
from rag_retriever import retrieve_relevant_docs
from sql_generator import generate_sql
from sql_validator import validate_and_rank_sql
from feedback_manager import log_feedback
import json

app = Flask(__name__, template_folder="templates", static_folder="static")

bq_client = bigquery.Client()
llm = pipeline("text2text-generation", model="google/flan-t5-large")

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")  # ✅ Serve the chatbot UI

@app.route("/query", methods=["POST"])
def query():
    user_input = request.json.get("query", "")
    if not user_input:
        return jsonify({"error": "Missing 'query' field in request"}), 400

    schema = get_bigquery_schema()
    # Open a file for writing in JSON mode
    with open('schema.json', 'w') as outfile:
    # Dump the dictionary to the file
        json.dump(schema, outfile)

    print("BigQuery schema saved to schema.json")
    print('------------------------------------query-------------------------------')
    print(user_input)
    print('------------------------------------query-------------------------------')
    relevant_docs = retrieve_relevant_docs(user_input, schema)
    sql_candidates = generate_sql(user_input, relevant_docs)
    best_sql = validate_and_rank_sql(sql_candidates)

    if not best_sql:
        return jsonify({"error": "Failed to generate a valid SQL query"}), 400

    try:
        query_job = bq_client.query(best_sql)
        results = query_job.result()
        data = [dict(row) for row in results]

        response = {
            "query": best_sql,
            "results": data,
            "explanation": "The query was generated based on similar past queries and schema details."
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": "BigQuery execution failed", "details": str(e)}), 500

@app.route("/feedback", methods=["POST"])
def feedback():
    feedback_data = request.json
    log_feedback(feedback_data)
    return jsonify({"message": "Feedback recorded, model will improve."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
