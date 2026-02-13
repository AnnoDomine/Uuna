# Tools/tests/toolset_tests/tools/tinker/test_tinker_tools.py
from unittest.mock import MagicMock
from Tools.toolsets.tools.tinker.assess_complexity import assess_complexity
from Tools.toolsets.tools.tinker.assign_potential_score import assign_potential_score

def test_assess_complexity_tier_1():
    result = assess_complexity("What is the ID of Spell X?")
    assert result["complexity_tier"] == 1

def test_assess_complexity_tier_3():
    # Multi-build + ambiguous
    result = assess_complexity("Compare cryptic Field_123 across all builds.")
    assert result["complexity_tier"] == 3
    assert "Multi-build analysis" in result["difficulty_factors"]

def test_assign_potential_score_success():
    mock_db = MagicMock()
    
    result = assign_potential_score(mock_db, "ev-123", 150)
    
    assert result["status"] == "success"
    assert result["max_potential"] == 150
    mock_db.execute.assert_called_once()
