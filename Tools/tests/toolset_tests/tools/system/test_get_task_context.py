# Tools/tests/toolset_tests/tools/system/test_get_task_context.py
from unittest.mock import MagicMock
from Tools.toolsets.tools.system.get_task_context import get_task_context


def test_get_task_context_success():
    mock_db = MagicMock()
    # Mock return for: task_id, query, status, event_id, target_role, output, confidence
    mock_db.execute.return_value.fetchall.return_value = [
        ("tk-123", "User Query", "active", "ev-1", "Archivist", '{"res": 1}', 0.9)
    ]

    result = get_task_context(mock_db, "tk-123")

    assert "task" in result
    assert result["task"]["task_id"] == "tk-123"
    assert result["task"]["status"] == "active"
    assert len(result["history"]) == 1
    assert result["history"][0]["agent"] == "Archivist"


def test_get_task_context_not_found():
    mock_db = MagicMock()
    mock_db.execute.return_value.fetchall.return_value = []

    result = get_task_context(mock_db, "tk-none")
    assert "error" in result
