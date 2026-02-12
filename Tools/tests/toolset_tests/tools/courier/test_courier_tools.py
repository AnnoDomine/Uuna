# Tools/tests/toolset_tests/tools/courier/test_courier_tools.py
import pytest
from unittest.mock import MagicMock
from Tools.toolsets.tools.courier.get_role_capabilities import get_role_capabilities
from Tools.toolsets.tools.courier.create_task_event import create_task_event
from Tools.toolsets.tools.courier.update_task_status import update_task_status

def test_get_role_capabilities_success():
    result = get_role_capabilities()
    
    assert "specialists" in result
    assert "archivist" in result["specialists"]
    assert "column_discovery" in result["specialists"]["archivist"]["tasks"]

def test_create_task_event_success():
    mock_db = MagicMock()
    
    result = create_task_event(mock_db, "tk-1", "Courier", "Archivist", {"input": "test"})
    
    assert result["status"] == "success"
    assert "event_id" in result
    assert result["target"] == "Archivist"
    mock_db.execute.assert_called_once()

def test_update_task_status_success():
    mock_db = MagicMock()
    
    result = update_task_status(mock_db, "tk-1", "active", "Archivist")
    
    assert result["status"] == "success"
    assert result["new_status"] == "active"
    assert result["current_location"] == "Archivist"
    mock_db.execute.assert_called_once()
