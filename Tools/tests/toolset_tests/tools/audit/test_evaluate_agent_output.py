# Tools/tests/toolset_tests/tools/audit/test_evaluate_agent_output.py
import pytest
from unittest.mock import MagicMock
from Tools.toolsets.tools.audit.evaluate_agent_output import evaluate_agent_output


@pytest.fixture
def mock_db_client():
    return MagicMock()


@pytest.fixture
def mock_ask_ai():
    return MagicMock()


def test_evaluate_agent_output_blind_scoring(mock_db_client, mock_ask_ai):
    # Setup:
    # 1. DB returns max_potential = 200 for this event
    mock_db_client.execute.return_value.fetchone.return_value = (200,)

    # 2. AI Observer awards 100 points
    mock_ask_ai.return_value = {
        "verdict": "Good enough.",
        "quality_score": 100,
        "honesty_rating": "Honest.",
        "sage_recommendation": "APPROVE",
    }

    agent_output = {"data": "test"}
    reported_confidence = 1.0  # 100 points / (200 pot * 1.0 conf) = 50%

    result = evaluate_agent_output(
        mock_db_client, mock_ask_ai, "task-123", "event-456", agent_output, reported_confidence
    )

    # Assertions: No absolute points in output
    assert "quality_score" not in result
    # CPP = 100 / 200 = 50%
    assert result["cpp_percent"] == 50.0
    # Personal = 100 / (200 * 1.0) = 50%
    assert result["personal_score_percent"] == 50.0
    assert result["recommendation"] == "APPROVE"


def test_evaluate_agent_output_low_confidence_bonus(mock_db_client, mock_ask_ai):
    # Setup: max_potential = 100
    mock_db_client.execute.return_value.fetchone.return_value = (100,)

    # AI awards 80 points
    mock_ask_ai.return_value = {
        "verdict": "Great.",
        "quality_score": 80,
        "honesty_rating": "Underestimated.",
        "sage_recommendation": "APPROVE",
    }

    # Agent was humble (0.5 confidence), but 0.7 floor applies
    # Personal Score = 80 / (100 * 0.7) = 114% -> capped at 100%
    result = evaluate_agent_output(mock_db_client, mock_ask_ai, "t", "e", {}, 0.5)

    assert result["personal_score_percent"] == 100.0
    assert result["cpp_percent"] == 80.0
