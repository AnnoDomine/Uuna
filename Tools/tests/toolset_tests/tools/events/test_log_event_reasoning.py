# Tools/tests/toolset_tests/tools/events/test_log_event_reasoning.py
from unittest.mock import MagicMock
from Tools.toolsets.tools.events.log_event_reasoning import log_event_reasoning


def test_log_event_reasoning_success():
    mock_db = MagicMock()

    result = log_event_reasoning(mock_db, "ev-1", "tk-1", "Role", "Message")

    assert result["status"] == "success"
    mock_db.execute.assert_called_once()
    args = mock_db.execute.call_args[0]
    assert "INSERT INTO research.event_logs" in args[0]
    assert args[1] == ["ev-1", "tk-1", "Role", "Message"]
