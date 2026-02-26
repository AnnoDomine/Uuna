# Tools/tests/toolset_tests/tools/events/test_get_event_data.py
from unittest.mock import patch
from Tools.toolsets.tools.events.get_event_data import get_event_data


def test_get_event_data_success():
    with patch("Tools.toolsets.tools.events.get_event_data.db") as mock_db:
        # Mock return for: event_id, task_id, initiator, target, input_data, confidence, max_potential
        mock_db.execute.return_value.fetchone.return_value = (
            "ev-123",
            "tk-456",
            "Courier",
            "Archivist",
            '{"job": "mine"}',
            0.8,
            100,
        )

        result = get_event_data("ev-123")

        assert result["event_id"] == "ev-123"
        assert result["target"] == "Archivist"
        assert result["input_data"]["job"] == "mine"
        assert result["max_potential"] == 100


def test_get_event_data_not_found():
    with patch("Tools.toolsets.tools.events.get_event_data.db") as mock_db:
        mock_db.execute.return_value.fetchone.return_value = None

        result = get_event_data("ev-none")
        assert "error" in result
