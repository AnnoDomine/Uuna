# Tools/tests/toolset_tests/tools/events/test_get_event_data.py
from unittest.mock import MagicMock
from Tools.toolsets.tools.events.get_event_data import get_event_data

def test_get_event_data_success():
    mock_db = MagicMock()
    # Mock return for: event_id, task_id, initiator, target, input_data, confidence, max_potential
    mock_db.execute.return_value.fetchone.return_value = (
        "ev-123", "tk-456", "Courier", "Archivist", '{"job": "mine"}', 0.8, 100
    )
    
    result = get_event_data(mock_db, "ev-123")
    
    assert result["event_id"] == "ev-123"
    assert result["target"] == "Archivist"
    assert result["input_data"]["job"] == "mine"
    assert result["max_potential"] == 100

def test_get_event_data_not_found():
    mock_db = MagicMock()
    mock_db.execute.return_value.fetchone.return_value = None
    
    result = get_event_data(mock_db, "ev-none")
    assert "error" in result
