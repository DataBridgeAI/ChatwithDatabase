import os
import pytest
import json
from unittest.mock import patch, MagicMock

import ai.llm as llm


def test_set_openai_api_key(monkeypatch):
    with patch("ai.llm.ChatOpenAI") as mock_llm:
        mock_instance = MagicMock()
        mock_llm.return_value = mock_instance

        llm.set_openai_api_key("fake-api-key")

        assert os.environ["OPENAI_API_KEY"] == "fake-api-key"
        mock_llm.assert_called_once_with(model_name="gpt-4", temperature=0.3)
        assert llm.llm == mock_instance


@patch("ai.llm.storage.Client")
def test_load_prompt_template(mock_storage_client):
    # Setup mock storage client and blob
    mock_blob = MagicMock()
    mock_blob.name = "prompts/prompt1.json"
    mock_blob.download_as_string.return_value = json.dumps({
        "template": "Generate SQL for: {user_query}"
    }).encode()

    mock_bucket = MagicMock()
    mock_bucket.list_blobs.return_value = [mock_blob]

    mock_storage = MagicMock()
    mock_storage.bucket.return_value = mock_bucket
    mock_storage_client.return_value = mock_storage

    llm.load_prompt_template("mock-bucket")

    assert llm.PROMPT_TEMPLATE == "Generate SQL for: {user_query}"


def test_clean_sql():
    raw = "```sql\nSELECT * FROM users;\n```"
    cleaned = llm.clean_sql(raw)
    assert cleaned == "SELECT * FROM users;"


@patch("ai.llm.llm")
@patch("ai.llm.PromptTemplate")
def test_generate_sql_success(mock_prompt_template, mock_llm_instance):
    llm.PROMPT_TEMPLATE = "Generate SQL for: {user_query}"

    mock_prompt = MagicMock()
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = MagicMock(content="```sql\nSELECT * FROM users;```")

    mock_prompt.__or__.return_value = mock_chain
    mock_prompt_template.return_value = mock_prompt

    result = llm.generate_sql("Show all users", "schema", "project", "dataset")

    assert result == "SELECT * FROM users;"


@patch("ai.llm.llm")
@patch("ai.llm.PromptTemplate")
def test_generate_sql_no_sql_keyword(mock_prompt_template, mock_llm_instance):
    llm.PROMPT_TEMPLATE = "Generate SQL for: {user_query}"

    mock_prompt = MagicMock()
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = MagicMock(content="I'm not sure what you're asking.")

    mock_prompt.__or__.return_value = mock_chain
    mock_prompt_template.return_value = mock_prompt

    with pytest.raises(ValueError, match="❌ Unable to generate SQL"):
        llm.generate_sql("random question", "schema", "project", "dataset")


def test_generate_sql_without_prompt_template():
    llm.PROMPT_TEMPLATE = None
    with pytest.raises(RuntimeError, match="Prompt template not loaded"):
        llm.generate_sql("query", "schema", "project", "dataset")
