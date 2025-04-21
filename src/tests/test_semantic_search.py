import pytest
import numpy as np
from unittest import mock
from promptfilter.semantic_search import (
    preprocess_text,
    extract_potential_schema_terms,
    find_fuzzy_matches,
    generate_user_input_embedding
)

def test_preprocess_text():
    input_text = "SELECT * FROM Customers WHERE CustomerID = 1;"
    expected = "select from customers where customerid 1"
    assert preprocess_text(input_text) == expected

@pytest.mark.parametrize("query,expected_terms", [
    ("SELECT name, age FROM users WHERE age > 30", {"name", "age", "users"}),
    ("SELECT * FROM orders JOIN customers ON orders.customer_id = customers.id", {"orders", "customers"}),
    ("SELECT total_price FROM sales WHERE date > '2023-01-01'", {"total_price", "sales", "date"})
])
def test_extract_potential_schema_terms(query, expected_terms):
    terms = extract_potential_schema_terms(query)
    assert set(terms) & expected_terms == expected_terms  # Ensure expected terms are present

def test_find_fuzzy_matches():
    schema_keys = [
        "orders:order_id", "orders:customer_id", "customers:name", "customers:email"
    ]
    query_terms = ["order", "email", "custmr"]
    
    results = find_fuzzy_matches(schema_keys, query_terms)
    matched_keys = {r["schema_element"] for r in results}
    assert "orders:order_id" in matched_keys
    assert "customers:email" in matched_keys
    assert any("customer" in r["schema_element"] for r in results)

@mock.patch("promptfilter.semantic_search.VertexAIEmbeddings")
def test_generate_user_input_embedding(mock_embed):
    mock_embed.return_value.embed_documents.return_value = [[0.1, 0.2, 0.3]]
    # Patch the actual model in the module namespace
    with mock.patch("promptfilter.semantic_search.embedding_model", mock_embed.return_value):
        from promptfilter.semantic_search import generate_user_input_embedding
        result = generate_user_input_embedding("Find customer name")
        np.testing.assert_array_almost_equal(result, np.array([0.1, 0.2, 0.3]))

