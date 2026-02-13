# Tools/tests/test_ai_client.py
import pytest
import responses
import json
from Tools.core.ai_client import AIClient


@pytest.fixture
def ai_client():
    return AIClient(ollama_url="http://mock-ollama/api/chat", model="test-model", debug=False)


@responses.activate
def test_ask_success(ai_client):
    # Setup mock response
    mock_response = {"message": {"content": json.dumps({"discovery": "Found a secret", "confidence": 0.95})}}
    responses.add(responses.POST, "http://mock-ollama/api/chat", json=mock_response, status=200)

    result = ai_client.ask("TestRole", "TestPrompt")

    assert result["discovery"] == "Found a secret"
    assert result["confidence"] == 0.95


@responses.activate
def test_ask_with_wrapper(ai_client):
    # Test that it handles wrapped JSON
    mock_response = {"message": {"content": json.dumps({"result": {"discovery": "Wrapped"}})}}
    responses.add(responses.POST, "http://mock-ollama/api/chat", json=mock_response, status=200)

    result = ai_client.ask("TestRole", "TestPrompt")

    assert result["discovery"] == "Wrapped"


@responses.activate
def test_ask_failure(ai_client):
    # Setup mock failure
    responses.add(responses.POST, "http://mock-ollama/api/chat", status=500)

    result = ai_client.ask("TestRole", "TestPrompt")

    assert result == {}


def test_robust_json_decode():
    client = AIClient()

    # Test dictionary input
    assert client.robust_json_decode({"a": 1}) == {"a": 1}

    # Test single-key wrapper
    assert client.robust_json_decode({"analysis": {"key": "val"}}) == {"key": "val"}

    # Test known wrappers
    assert client.robust_json_decode({"query_analysis": {"x": 1}}) == {"x": 1}

    # Test non-dict
    assert client.robust_json_decode("string") == {}
