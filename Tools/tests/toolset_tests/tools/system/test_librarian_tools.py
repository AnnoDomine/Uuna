# Tools/tests/toolset_tests/tools/system/test_librarian_tools.py
import pytest
from unittest.mock import MagicMock
from Tools.toolsets.tools.system.create_research_task import create_research_task
from Tools.toolsets.tools.system.get_verified_results import get_verified_results

def test_create_research_task_success():
    mock_db = MagicMock()
    
    result = create_research_task(mock_db, "Tell me about Uuna", ["7.3.5.25600"])
    
    assert result["status"] == "success"
    assert "task_id" in result
    mock_db.execute.assert_called_once()

def test_get_verified_results_success():
    mock_db = MagicMock()
    # Mock return for: initiator_role, target_role, output_data, agent_confidence
    mock_db.execute.return_value.fetchall.return_value = [
        ("Courier", "Archivist", {"id": 123}, 0.95),
        ("Courier", "Expedition Group", {"lore": "Uuna is a ghost"}, 0.9)
    ]
    
    result = get_verified_results(mock_db, "tk-1")
    
    assert result["task_id"] == "tk-1"
    assert result["count"] == 2
    assert result["findings"][0]["source_agent"] == "Archivist"
    assert "lore" in result["findings"][1]["data"]
