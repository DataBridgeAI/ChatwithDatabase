import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys
import os

# Import the functions we want to test
from model_validation import fetch_evaluation_data, evaluate_and_store_metrics

class TestModelValidation(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_data = pd.DataFrame({
            "generated_sql": ["SELECT * FROM sales", "SELECT name FROM customers"],
            "correct_sql": ["SELECT * FROM sales", "SELECT name FROM customers"],
            "feedback": [1, 0]  # Mocked user feedback (1=correct, 0=incorrect)
        })

    @patch('model_validation.client')
    def test_fetch_evaluation_data(self, mock_client):
        """Test fetching evaluation data from BigQuery."""
        # Configure the mock
        mock_query = MagicMock()
        mock_query.to_dataframe.return_value = self.mock_data
        mock_client.query.return_value = mock_query

        # Call the function
        result = fetch_evaluation_data()

        # Assertions
        self.assertEqual(len(result), 2)
        self.assertEqual(list(result.columns), ["generated_sql", "correct_sql", "feedback"])
        mock_client.query.assert_called_once()

    @patch('model_validation.fetch_evaluation_data')
    def test_evaluate_and_store_metrics(self, mock_fetch):
        """Test the evaluation process and metric storage."""
        # Configure the mock
        mock_fetch.return_value = pd.DataFrame({
            "generated_sql": ["SELECT * FROM products"],
            "correct_sql": ["SELECT * FROM products"],
            "feedback": [1]  # Mocked feedback (1 = correct)
        })

        # Run the function
        with patch('model_validation.store_metrics_in_bigquery') as mock_store:
            evaluate_and_store_metrics()
            mock_store.assert_called_once()
            
            # Verify the metrics structure
            called_args = mock_store.call_args[0][0]
            self.assertIsInstance(called_args, dict)
            self.assertIn('precision', called_args)
            self.assertIn('recall', called_args)
            self.assertIn('f1_score', called_args)
            self.assertIn('total_samples', called_args)
            self.assertIn('correct_predictions', called_args)
            self.assertIn('incorrect_predictions', called_args)

if __name__ == "__main__":
    unittest.main()