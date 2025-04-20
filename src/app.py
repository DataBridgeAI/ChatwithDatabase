from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import time
import os
import json
import tempfile
import uuid
from dotenv import load_dotenv
import json
from io import BytesIO

from database.query_executor import execute_bigquery_query
from database.schema import get_bigquery_schema
from database.chat_history import init_chat_history_db, get_chat_history_db
from ai.llm import generate_sql, load_prompt_template, set_openai_api_key
from feedback.feedback_manager import store_feedback
from feedback.vector_search import retrieve_similar_query
from feedback.chroma_setup import download_and_extract_chromadb
from monitoring.mlflow_config import QueryTracker
from query_checks.content_checker import sensitivity_filter
from promptfilter.semantic_search import download_and_prepare_embeddings, check_query_relevance
from ai.data_formatter import dataframe_to_json
from monitoring_utils import GCPMonitoring

project_id = os.environ.get('PROJECT_ID')
monitor = GCPMonitoring(project_id)
# Load environment variables from .env file
load_dotenv('src/.env')

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Setup credentials from environment variables
def setup_credentials():
    try:
        # Setup OpenAI API key if available in environment
        if "OPENAI_API_KEY" in os.environ:
            openai_api_key = os.environ["OPENAI_API_KEY"]
            set_openai_api_key(openai_api_key)
            print("OpenAI API key loaded from environment")
        
        # If credentials JSON is provided directly
        if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
            credentials_json = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
            
            # Create a temporary file to store the credentials
            fd, temp_path = tempfile.mkstemp(suffix='.json')
            with os.fdopen(fd, 'w') as tmp:
                json.dump(credentials_json, tmp)
                
            # Set the environment variable
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
            print("Google credentials loaded from environment JSON")
            return True
            
        # If direct path is provided
        elif "GOOGLE_APPLICATION_CREDENTIALS" in os.environ and os.path.exists(os.environ["GOOGLE_APPLICATION_CREDENTIALS"]):
            print(f"Using Google credentials from: {os.environ['GOOGLE_APPLICATION_CREDENTIALS']}")
            return True
            
        print("Warning: Google credentials not found in environment")
        return False
    except Exception as e:
        print(f"Error setting up credentials: {str(e)}")
        return False

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

# Setup credentials during startup
try:
    if setup_credentials():
        print("Credentials setup successfully")
    else:
        print("Warning: Credentials not fully configured")
except Exception as e:
    print(f"Failed to setup credentials: {str(e)}")

# Initialize the query tracker
query_tracker = QueryTracker()

# Initialize the chat history database
try:
    init_chat_history_db("src/database/chat_history.db")
    print("Chat history database initialized")
except Exception as e:
    print(f"Failed to initialize chat history database: {str(e)}")

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
        project_id = data.get('project_id') or os.environ.get('PROJECT_ID')
        dataset_id = data.get('dataset_id') or os.environ.get('DATASET_ID')
        
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
        validation_error = sensitivity_filter(user_query)
        if validation_error:
            return jsonify({'error': validation_error}), 400

        query_relevance_flag = check_query_relevance(
            user_query,
            schema_embeddings=schema_embeddings
        )
        if not query_relevance_flag:
            return jsonify({'error': ' ❌ Query appears unrelated to the database schema'}), 400

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
def generate_query():
    data = request.json
    user_query = data.get('query')
    schema = data.get('schema')
    project_id = data.get('project_id') or os.environ.get('PROJECT_ID')
    dataset_id = data.get('dataset_id') or os.environ.get('DATASET_ID')
    conversation_id = data.get('conversation_id')
    
    # Generate a unique user ID if not provided
    user_id = data.get('user_id', str(uuid.uuid4()))

    if not all([user_query, schema, project_id, dataset_id]):
        return jsonify({'error': 'All fields are required'}), 400

    start_time = time.time()
    error = None
    query_execution_time = 0
    result_data = None

    try:
        # Generate SQL
        try:
            generated_sql = generate_sql(
                user_query=user_query,
                schema=schema,
                project_id=project_id,
                dataset_id=dataset_id
            )
        except ValueError as ve:
            return jsonify({
                'error': str(ve),
                'conversation_id': conversation_id
            }), 400

        # Execute SQL
        result_df, query_execution_time = execute_bigquery_query(generated_sql)
        monitor.log_event("Query execution completed successfully.")
        monitor.log_custom_metric("query_execution_time", '1')
        monitor.log_event("Sent metric: query_execution_time = 1")
        # Handle chat history
        db = get_chat_history_db()
        
        # Create a new conversation if one wasn't provided
        if not conversation_id:
            conversation_id = db.create_conversation(user_id, project_id, dataset_id)

        # Convert DataFrame to list of dictionaries for JSON serialization
        if result_df.empty or "Error" in result_df.columns:
            if "Error" in result_df.columns:
                error = result_df["Error"][0]
                
                # Store the error in chat history
                db.add_message(conversation_id, user_query, generated_sql, None)
                
                return jsonify({
                    'error': error,
                    'generated_sql': generated_sql,
                    'conversation_id': conversation_id
                }), 400
            else:
                # Store empty result in chat history
                db.add_message(conversation_id, user_query, generated_sql, [])
                
                return jsonify({
                    'error': 'No data returned',
                    'generated_sql': generated_sql,
                    'conversation_id': conversation_id
                }), 400
        else:
            # Convert to JSON using the data formatter
            result_data = dataframe_to_json(result_df)
            column_types = {col: str(dtype) for col, dtype in result_df.dtypes.items()}
            
            # Store the successful query in chat history
            db.add_message(conversation_id, user_query, generated_sql, result_data)

            return jsonify({
                'generated_sql': generated_sql,
                'results': result_data,
                'column_types': column_types,
                'columns': list(result_df.columns),
                'execution_time': query_execution_time,
                'conversation_id': conversation_id
            })
    except Exception as e:
        error = str(e)
        
        # Store the error in chat history if conversation exists
        if conversation_id:
            db = get_chat_history_db()
            db.add_message(
                conversation_id, 
                user_query, 
                generated_sql if 'generated_sql' in locals() else None, 
                None
            )
            
        return jsonify({
            'error': error,
            'generated_sql': generated_sql if 'generated_sql' in locals() else None,
            'conversation_id': conversation_id
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
                'project': project_id,
                'conversation_id': conversation_id
            }
        )

@app.route('/api/query/execute', methods=['POST'])
def execute_sql_query():
    data = request.json
    sql_query = data.get('sql')
    conversation_id = data.get('conversation_id')
    user_query = data.get('user_query', 'Custom SQL execution')

    if not sql_query:
        return jsonify({'error': 'SQL query is required'}), 400

    try:
        result_df, query_execution_time = execute_bigquery_query(sql_query)

        # Handle chat history if a conversation ID is provided
        if conversation_id:
            db = get_chat_history_db()

        if result_df.empty or "Error" in result_df.columns:
            if "Error" in result_df.columns:
                error = result_df["Error"][0]
                
                # Store the error in chat history if a conversation ID exists
                if conversation_id:
                    db.add_message(conversation_id, user_query, sql_query, None)
                
                return jsonify({
                    'error': error
                }), 400
            else:
                # Store empty result in chat history if a conversation ID exists
                if conversation_id:
                    db.add_message(conversation_id, user_query, sql_query, [])
                
                return jsonify({
                    'error': 'No data returned'
                }), 400
        else:
            # Convert to list of dicts for JSON serialization
            result_data = result_df.to_dict(orient='records')
            column_types = {col: str(dtype) for col, dtype in result_df.dtypes.items()}
            
            # Store the successful query in chat history if a conversation ID exists
            if conversation_id:
                db.add_message(conversation_id, user_query, sql_query, result_data)

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

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    user_id = request.args.get('user_id')
    limit = request.args.get('limit', 5, type=int)
    
    try:
        db = get_chat_history_db()
        conversations = db.get_recent_conversations(user_id, limit)
        
        return jsonify({
            'success': True,
            'conversations': conversations
        })
    except Exception as e:
        app.logger.error(f"Error fetching chat history: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'conversations': []
        }), 500

@app.route('/api/chat/conversation/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    try:
        db = get_chat_history_db()
        messages = db.get_conversation(conversation_id)
        details = db.get_conversation_details(conversation_id)
        
        if not details:
            return jsonify({
                'success': False,
                'error': 'Conversation not found',
                'messages': [],
                'details': {}
            }), 404
            
        return jsonify({
            'success': True,
            'details': details,
            'messages': messages
        })
    except Exception as e:
        app.logger.error(f"Error fetching conversation: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'messages': [],
            'details': {}
        }), 500

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
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/debug/conversations', methods=['GET'])
def debug_conversations():
    """Debug endpoint to check conversation data."""
    try:
        db = get_chat_history_db()
        
        # Get counts from database
        conn = db._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conversation_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM messages")
        message_count = cursor.fetchone()[0]
        
        # Get all conversations with details
        cursor.execute("""
            SELECT c.id, c.timestamp, c.project_id, c.dataset_id, 
                   COUNT(m.id) as message_count
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            GROUP BY c.id
            ORDER BY c.timestamp DESC
        """)
        
        conversations = [dict(row) for row in cursor.fetchall()]
        
        # Get the conversations that would be returned by get_recent_conversations
        recent = db.get_recent_conversations(limit=10)
        
        return jsonify({
            'success': True,
            'conversation_count': conversation_count,
            'message_count': message_count,
            'conversations': conversations,
            'recent_conversations': recent
        })
    except Exception as e:
        app.logger.error(f"Error in debug endpoint: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

#download the results as json file
@app.route('/api/query/download', methods=['POST'])
def download_results():
    try:
        data = request.json
        if not data or 'results' not in data:
            return jsonify({'error': 'No results provided'}), 400
            
        result_df = pd.DataFrame(data['results'])
        
        try:
            # Convert to JSON using the data formatter
            json_data = dataframe_to_json(result_df)
            json_str = json.dumps(json_data, indent=2)
        except Exception as format_error:
            return jsonify({'error': str(format_error)}), 500
        
        # Create a BytesIO object
        buffer = BytesIO()
        buffer.write(json_str.encode())
        buffer.seek(0)
        
        # Create response with the file
        response = send_file(
            buffer,
            mimetype='application/json',
            as_attachment=True,
            download_name='query_results.json'
        )
        
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
