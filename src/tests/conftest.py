import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src directory to Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Mock OpenAI API key environment variable
os.environ["OPENAI_API_KEY"] = "test-key"

@pytest.fixture(autouse=True)
def mock_global_dependencies():
    # Create mock modules
    mock_sentence_transformers = MagicMock()
    mock_chromadb = MagicMock()
    mock_openai = MagicMock()

    # Create the module patches
    patches = [
        patch('sentence_transformers.SentenceTransformer', return_value=MagicMock()),
        patch('chromadb.PersistentClient', return_value=MagicMock()),
        patch('langchain_openai.ChatOpenAI', return_value=MagicMock()),
        patch.dict('sys.modules', {
            'sentence_transformers': mock_sentence_transformers,
            'chromadb': mock_chromadb,
            'openai': mock_openai
        })
    ]

    # Start all patches
    for p in patches:
        p.start()
    
    yield

    # Stop all patches
    for p in patches:
        p.stop()

@pytest.fixture
def mock_bigquery_client():
    with patch('google.cloud.bigquery.Client') as mock:
        mock.return_value = MagicMock()
        yield mock

@pytest.fixture
def mock_storage_client():
    with patch('google.cloud.storage.Client') as mock:
        mock.return_value = MagicMock()
        yield mock




