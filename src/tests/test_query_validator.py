import unittest
import numpy as np
from unittest.mock import patch
import sys
import os

# Add the parent directory to Python's path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from promptfilter.semantic_search import (
    check_query_relevance,
    generate_user_input_embedding,
    download_and_prepare_embeddings
)

class TestQueryRelevance(unittest.TestCase):

    @patch('promptfilter.semantic_search.download_and_prepare_embeddings')
    @patch('promptfilter.semantic_search.generate_user_input_embedding')
    def test_relevant_query(self, mock_generate_embedding, mock_download_embeddings):
        """Test if a relevant query is correctly identified."""
        # Mock schema embeddings
        mock_download_embeddings.return_value = {
            "customers": {"embedding": np.array([0.1, 0.2, 0.3]), "semantic_text": "customer information"},
            "orders": {"embedding": np.array([0.4, 0.5, 0.6]), "semantic_text": "order details"},
        }

        # Mock user input embedding (similar to "orders" embedding)
        mock_generate_embedding.return_value = np.array([0.4, 0.5, 0.6])

        result = check_query_relevance("Show me all orders")
        self.assertTrue(result)

    @patch('promptfilter.semantic_search.download_and_prepare_embeddings')
    @patch('promptfilter.semantic_search.generate_user_input_embedding')
    def test_irrelevant_query(self, mock_generate_embedding, mock_download_embeddings):
        """Test if an irrelevant query is correctly identified."""
        # Create orthogonal vectors to ensure low similarity
        mock_download_embeddings.return_value = {
            "customers": {
                "embedding": np.array([1.0, 0.0, 0.0]),
                "semantic_text": "customer information"
            },
            "orders": {
                "embedding": np.array([0.0, 1.0, 0.0]),
                "semantic_text": "order details"
            },
        }

        # This vector is more similar to [0, 0, 1] which is orthogonal to both stored embeddings
        mock_generate_embedding.return_value = np.array([0.0, 0.0, 1.0])

        result = check_query_relevance("Tell me a joke", threshold=0.75)
        self.assertFalse(result)

    @patch('promptfilter.semantic_search.download_and_prepare_embeddings')
    @patch('promptfilter.semantic_search.generate_user_input_embedding')
    def test_edge_case_empty_input(self, mock_generate_embedding, mock_download_embeddings):
        """Test edge case: empty input should return False."""
        mock_download_embeddings.return_value = {
            "products": {"embedding": np.array([0.3, 0.3, 0.3]), "semantic_text": "product details"},
        }

        mock_generate_embedding.return_value = np.array([0.0, 0.0, 0.0])

        result = check_query_relevance("")
        self.assertFalse(result)

    @patch('promptfilter.semantic_search.download_and_prepare_embeddings')
    @patch('promptfilter.semantic_search.generate_user_input_embedding')
    def test_threshold_behavior(self, mock_generate_embedding, mock_download_embeddings):
        """Test if threshold works correctly."""
        # Use unit vectors for clearer similarity calculation
        mock_download_embeddings.return_value = {
            "employees": {
                "embedding": np.array([1.0, 0.0, 0.0]),
                "semantic_text": "employee records"
            },
        }

        # This will have a cosine similarity of approximately 0.87 with [1,0,0]
        mock_generate_embedding.return_value = np.array([0.5, 0.5, 0.0])

        result = check_query_relevance("HR details", threshold=0.90)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
