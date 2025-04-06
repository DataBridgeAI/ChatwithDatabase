from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import time
import os
import json
import tempfile

from database.query_executor import execute_bigquery_query
from database.schema import get_bigquery_schema
from ai.llm import generate_sql, load_prompt_template, set_openai_api_key
from feedback.feedback_manager import store_feedback
from feedback.vector_search import retrieve_similar_query
from feedback.chroma_setup import download_and_extract_chromadb
from monitoring.mlflow_config import QueryTracker
from query_checks.content_checker import validate_query
from promptfilter.semantic_search import download_and_prepare_embeddings, check_query_relevance

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize schema embeddings at startup
try:
    schema_embeddings = download_and_prepare_embeddings()
    if not schema_embeddings:
        print("Failed to load schema embeddings")
except Exception as e:
    print(f"Failed to initialize schema embeddings: {str(e)}")

# Setup ChromaDB at startup
try:
    download_and_extract_chromadb()
except Exception as e:
    print(f"Failed to setup ChromaDB: {str(e)}")

# Load prompt template at startup
try:
    load_prompt_template()
except Exception as e:
    print(f"Failed to load prompt template: {str(e)}")

# Initialize the query tracker
query_tracker = QueryTracker()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/api/credentials', methods=['POST'])
def set_credentials():
    data = request.json
    openai_api_key = data.get('openai_api_key')
    google_credentials = data.get('google_credentials')

    response = {"success": False, "messages": []}

    # Handle OpenAI API key
    if openai_api_key:
        try:
            # Set the API key in the LLM module
            set_openai_api_key(openai_api_key)
            os.environ["OPENAI_API_KEY"] = openai_api_key
            response["messages"].append("OpenAI API key set successfully")
            response["openai_success"] = True
        except Exception as e:
            response["messages"].append(f"Failed to set OpenAI API key: {str(e)}")
            response["openai_success"] = False

    # Handle Google credentials
    if google_credentials:
        try:
            # Create a temporary file to store the credentials
            fd, temp_path = tempfile.mkstemp(suffix='.json')
            with os.fdopen(fd, 'w') as tmp:
                json.dump(google_credentials, tmp)

            # Set the environment variable to point to this file
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
            response["messages"].append("Google credentials set successfully")
            response["google_success"] = True
        except Exception as e:
            response["messages"].append(f"Failed to set Google credentials: {str(e)}")
            response["google_success"] = False

    response["success"] = response.get("openai_success", False) or response.get("google_success", False)
    return jsonify(response)

@app.route('/api/schema', methods=['POST'])
def fetch_schema():
    try:
        data = request.json
        project_id = data.get('project_id')
        dataset_id = data.get('dataset_id')
        
        app.logger.info(f"Received schema request for project: {project_id}, dataset: {dataset_id}")
        
        if not project_id or not dataset_id:
            return jsonify({'error': 'Project ID and Dataset ID are required'}), 400
        
        try:
            app.logger.info("Calling get_bigquery_schema function")
            schema = get_bigquery_schema(project_id, dataset_id)
            app.logger.info(f"Schema retrieved: {bool(schema)}")
            
            if schema:
                return jsonify({'schema': schema})
            else:
                app.logger.error("Schema is empty or None")
                return jsonify({'error': 'Failed to fetch schema - empty result'}), 500
        except Exception as e:
            app.logger.error(f"Error in get_bigquery_schema: {str(e)}")
            import traceback
            app.logger.error(traceback.format_exc())
            return jsonify({'error': f"Schema fetch error: {str(e)}"}), 500
    except Exception as e:
        app.logger.error(f"General endpoint error: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({'error': f"Server error: {str(e)}"}), 500

@app.route('/api/query/validate', methods=['POST'])
def validate_user_query():
    data = request.json
    user_query = data.get('query')

    if not user_query:
        return jsonify({'error': 'Query is required'}), 400

    try:
        validation_error = validate_query(user_query)
        if validation_error:
            return jsonify({'error': validation_error}), 400

        query_relevance_flag = check_query_relevance(
            user_query,
            schema_embeddings=schema_embeddings
        )
        if not query_relevance_flag:
            return jsonify({'error': 'Query appears unrelated to the database schema'}), 400

        return jsonify({'valid': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/query/similar', methods=['POST'])
def find_similar_query():
    data = request.json
    user_query = data.get('query')

    if not user_query:
        return jsonify({'error': 'Query is required'}), 400

    try:
        similar_query, past_sql = retrieve_similar_query(user_query)

        if similar_query and past_sql:
            return jsonify({
                'found': True,
                'similar_query': similar_query,
                'past_sql': past_sql
            })
        else:
            return jsonify({'found': False})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/query/generate', methods=['POST'])
def generate_and_execute_query():
    data = request.json
    user_query = data.get('query')
    schema = data.get('schema')
    project_id = data.get('project_id')
    dataset_id = data.get('dataset_id')

    if not all([user_query, schema, project_id, dataset_id]):
        return jsonify({'error': 'All fields are required'}), 400

    start_time = time.time()
    error = None
    query_execution_time = 0

    try:
        # Generate SQL
        generated_sql = generate_sql(
            user_query,
            schema,
            project_id,
            dataset_id
        )

        # Execute SQL
        result_df, query_execution_time = execute_bigquery_query(generated_sql)

        # Convert DataFrame to list of dictionaries for JSON serialization
        if result_df.empty or "Error" in result_df.columns:
            if "Error" in result_df.columns:
                error = result_df["Error"][0]
                return jsonify({
                    'error': error,
                    'generated_sql': generated_sql
                }), 400
            else:
                return jsonify({
                    'error': 'No data returned',
                    'generated_sql': generated_sql
                }), 400
        else:
            # Convert to list of dicts for JSON serialization
            result_data = result_df.to_dict(orient='records')
            column_types = {col: str(dtype) for col, dtype in result_df.dtypes.items()}

            return jsonify({
                'generated_sql': generated_sql,
                'results': result_data,
                'column_types': column_types,
                'columns': list(result_df.columns),
                'execution_time': query_execution_time
            })
    except Exception as e:
        error = str(e)
        return jsonify({
            'error': error,
            'generated_sql': generated_sql if 'generated_sql' in locals() else None
        }), 500
    finally:
        total_time = time.time() - start_time

        # Log query execution details
        query_tracker.log_query_execution(
            user_query=user_query,
            generated_sql=generated_sql if 'generated_sql' in locals() else None,
            execution_time=query_execution_time,
            total_time=total_time,
            query_result=result_df if 'result_df' in locals() else None,
            error=error,
            metadata={
                'dataset': dataset_id,
                'project': project_id
            }
        )

@app.route('/api/set-credentials-path', methods=['POST'])
def set_credentials_path():
    data = request.json
    credentials_path = data.get('credentials_path')
    
    if not credentials_path:
        return jsonify({'error': 'Credentials path is required'}), 400
        
    try:
        # Set the environment variable
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        app.logger.info(f"Set GOOGLE_APPLICATION_CREDENTIALS to {credentials_path}")
        
        # Check if the file exists
        if os.path.exists(credentials_path):
            return jsonify({
                'success': True,
                'message': f'Credentials path set to {credentials_path}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Credentials file not found at {credentials_path}'
            }), 400
    except Exception as e:
        app.logger.error(f"Error setting credentials path: {str(e)}")
        return jsonify({'error': str(e)}), 500@app.route('/api/query/execute', methods=['POST'])
def execute_sql_query():
    data = request.json
    sql_query = data.get('sql')

    if not sql_query:
        return jsonify({'error': 'SQL query is required'}), 400

    try:
        result_df, query_execution_time = execute_bigquery_query(sql_query)

        if result_df.empty or "Error" in result_df.columns:
            if "Error" in result_df.columns:
                return jsonify({
                    'error': result_df["Error"][0]
                }), 400
            else:
                return jsonify({
                    'error': 'No data returned'
                }), 400
        else:
            # Convert to list of dicts for JSON serialization
            result_data = result_df.to_dict(orient='records')
            column_types = {col: str(dtype) for col, dtype in result_df.dtypes.items()}

            return jsonify({
                'results': result_data,
                'column_types': column_types,
                'columns': list(result_df.columns),
                'execution_time': query_execution_time
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    user_query = data.get('query')
    generated_sql = data.get('sql')
    feedback = data.get('feedback')
    execution_success = data.get('execution_success', False)

    if not all([user_query, generated_sql, feedback]):
        return jsonify({'error': 'All fields are required'}), 400

    try:
        store_feedback(user_query, generated_sql, feedback, execution_success=execution_success)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)