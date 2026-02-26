# Tools/tests/toolsets/tools/registry/test_check_build_status.py
import pytest
from unittest.mock import patch
from Tools.toolsets.tools.registry.check_build_status import check_build_status


@pytest.fixture
def mock_db():
    with patch("Tools.toolsets.tools.registry.check_build_status.db") as mocked_db:
        yield mocked_db


def test_check_build_status_not_found(mock_db):
    # Setup: DB returns no result for the version
    mock_db.execute.return_value.fetchone.return_value = None

    result = check_build_status("9.9.9.99999")

    assert result["exists"] is False
    assert result["is_downloaded"] is False
    assert "unknown" in result["message"]


def test_check_build_status_ready(mock_db):
    # Setup: DB returns downloaded=True, indexed=True
    mock_db.execute.return_value.fetchone.return_value = ("7.3.5.25600", True, True)

    result = check_build_status("7.3.5.25600")

    assert result["exists"] is True
    assert result["is_downloaded"] is True
    assert result["is_indexed"] is True
    assert "ready" in result["message"]


def test_check_build_status_not_ready(mock_db):
    # Setup: DB returns downloaded=True, indexed=False
    mock_db.execute.return_value.fetchone.return_value = ("8.0.1.27101", True, False)

    result = check_build_status("8.0.1.27101")

    assert result["exists"] is True
    assert result["is_downloaded"] is True
    assert result["is_indexed"] is False
    assert "not fully available" in result["message"]


def test_check_build_status_error(mock_db):
    # Setup: DB execution fails
    mock_db.execute.side_effect = Exception("DB Error")

    result = check_build_status("1.12.1")

    assert "error" in result
    assert result["exists"] is False
