import sqlite3
import json
from datetime import datetime
import os
import threading

# Thread-local storage for database connections
local_storage = threading.local()

class ChatHistoryDB:
    def __init__(self, db_path="chat_history.db"):
        # Make sure the directory exists
        directory = os.path.dirname(os.path.abspath(db_path))
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        self.db_path = db_path
        self._create_tables()
    
    def _get_connection(self):
        """Get a thread-local database connection."""
        if not hasattr(local_storage, 'connection') or local_storage.connection is None:
            # Create a new connection for this thread
            local_storage.connection = sqlite3.connect(self.db_path)
            local_storage.connection.row_factory = sqlite3.Row
        
        return local_storage.connection
    
    def _get_cursor(self):
        """Get a cursor from the thread-local connection."""
        return self._get_connection().cursor()
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp TEXT,
            project_id TEXT,
            dataset_id TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            user_query TEXT,
            generated_sql TEXT,
            results TEXT,
            timestamp TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
        ''')
        
        conn.commit()
    
    def create_conversation(self, user_id, project_id, dataset_id):
        """Create a new conversation and return its ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO conversations (user_id, timestamp, project_id, dataset_id) VALUES (?, ?, ?, ?)",
            (user_id, timestamp, project_id, dataset_id)
        )
        conn.commit()
        
        return cursor.lastrowid
    
    def add_message(self, conversation_id, user_query, generated_sql, results):
        """Add a new message to an existing conversation."""
        conn = self._get_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        results_json = json.dumps(results) if results else None
        
        cursor.execute(
            "INSERT INTO messages (conversation_id, user_query, generated_sql, results, timestamp) VALUES (?, ?, ?, ?, ?)",
            (conversation_id, user_query, generated_sql, results_json, timestamp)
        )
        conn.commit()
        
        return cursor.lastrowid
    
    def get_conversation(self, conversation_id):
        """Get all messages for a specific conversation."""
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp",
            (conversation_id,)
        )
        messages = [dict(row) for row in cursor.fetchall()]
        
        # Parse JSON results
        for message in messages:
            if message['results']:
                try:
                    message['results'] = json.loads(message['results'])
                except json.JSONDecodeError:
                    message['results'] = None
        
        return messages
    
    def get_conversation_details(self, conversation_id):
        """Get details about the conversation."""
        cursor = self._get_cursor()
        cursor.execute(
            "SELECT * FROM conversations WHERE id = ?",
            (conversation_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_recent_conversations(self, user_id=None, limit=5):
        """
        Get the most recent conversations, optionally filtered by user_id.
        Always returns exactly `limit` or fewer conversations, sorted by most recent first.
        """
        cursor = self._get_cursor()
    
        try:
            # Get conversations directly, ordered by most recent timestamp first
            if user_id:
                query = """
                SELECT * FROM conversations 
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """
                cursor.execute(query, (user_id, limit))
            else:
                query = """
                SELECT * FROM conversations
                ORDER BY timestamp DESC
                LIMIT ?
                """
                cursor.execute(query, (limit,))
        
            # Fetch the top conversations based on timestamp
            conversations = [dict(row) for row in cursor.fetchall()]
        
            # For each conversation, fetch the most recent query
            for conversation in conversations:
                cursor.execute(
                    """
                    SELECT user_query FROM messages
                    WHERE conversation_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                    """,
                    (conversation['id'],)
                )

                result = cursor.fetchone()
                conversation['user_query'] = result['user_query'] if result else 'No query found'
            
            return conversations
        except Exception as e:
            print(f"Error fetching recent conversations: {e}")
            import traceback
            print(traceback.format_exc())
            return []
    
    def close(self):
        """Close the database connection for this thread."""
        if hasattr(local_storage, 'connection') and local_storage.connection:
            local_storage.connection.close()
            local_storage.connection = None

# Global instance to be used throughout the application
_db_path = None

def init_chat_history_db(db_path="chat_history.db"):
    """Initialize the chat history database."""
    global _db_path
    _db_path = db_path
    # Test creating a connection
    db = ChatHistoryDB(db_path)
    return db

def get_chat_history_db():
    """Get the chat history database instance."""
    global _db_path
    if _db_path is None:
        _db_path = "chat_history.db"
    return ChatHistoryDB(_db_path)