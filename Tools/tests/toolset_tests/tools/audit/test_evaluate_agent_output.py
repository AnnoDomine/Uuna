# Tools/tests/toolsets/tools/audit/test_evaluate_agent_output.py
import pytest
from unittest.mock import MagicMock
from Tools.toolsets.tools.audit.evaluate_agent_output import evaluate_agent_output

@pytest.fixture
def mock_db_client():
    return MagicMock()

@pytest.fixture
def mock_ask_ai():
    return MagicMock()

def test_evaluate_agent_output_success(mock_db_client, mock_ask_ai):
    # Setup
    mock_ask_ai.return_value = {
        "verdict": "Excellent work.",
        "quality_score": 95,
        "honesty_rating": "Very honest.",
        "sage_recommendation": "APPROVE"
    }
    
    agent_output = {"data": "test"}
    reported_confidence = 0.9
    
    result = evaluate_agent_output(
        mock_db_client, 
        mock_ask_ai, 
        "task-123", 
        "event-456", 
        agent_output, 
        reported_confidence
    )
    
    assert result["quality_score"] == 95
    assert result["personal_score_percent"] > 0
    assert result["cpp_percent"] == 95.0
    assert result["recommendation"] == "APPROVE"

def test_evaluate_agent_output_overconfidence_penalty(mock_db_client, mock_ask_ai):
    # Setup: High confidence (1.0) but low score (50)
    mock_ask_ai.return_value = {
        "verdict": "Fail.",
        "quality_score": 50,
        "honesty_rating": "Too confident.",
        "sage_recommendation": "BLOCK"
    }
    
    agent_output = {"data": "bad"}
    reported_confidence = 1.0 # Effective confidence floor is 0.7 anyway
    
    result = evaluate_agent_output(
        mock_db_client, 
        mock_ask_ai, 
        "task-123", 
        "event-456", 
        agent_output, 
        reported_confidence
    )
    
    # personal_score = (50 / (100 * 1.0)) * 100 = 50%
    assert result["personal_score_percent"] == 50.0
    assert result["cpp_percent"] == 50.0

def test_evaluate_agent_output_low_confidence_floor(mock_db_client, mock_ask_ai):
    # Setup: Very low confidence (0.1) but good score (70)
    # The 0.7 floor should apply
    mock_ask_ai.return_value = {
        "verdict": "Good.",
        "quality_score": 70,
        "honesty_rating": "Underestimated.",
        "sage_recommendation": "APPROVE"
    }
    
    agent_output = {"data": "ok"}
    reported_confidence = 0.1 
    
    result = evaluate_agent_output(
        mock_db_client, 
        mock_ask_ai, 
        "task-123", 
        "event-456", 
        agent_output, 
        reported_confidence
    )
    
    # Effective confidence = 0.7
    # personal_score = (70 / (100 * 0.7)) * 100 = 100%
    assert result["personal_score_percent"] == 100.0
    assert result["cpp_percent"] == 70.0
