# Tools/tests/test_update_settings.py
from unittest.mock import patch
from Tools.core.update_settings import set_setting


@patch("Tools.core.update_settings.DBClient")
def test_set_setting_success(MockDBClient):
    mock_client = MockDBClient.return_value

    set_setting("threads", 10)

    # Verify DBClient was called with correct SQL and params
    args, _ = mock_client.execute.call_args
    assert "INSERT INTO registry.settings" in args[0]
    assert args[1] == ["threads", "10"]


@patch("Tools.core.update_settings.DBClient")
def test_set_setting_failure(MockDBClient):
    mock_client = MockDBClient.return_value
    mock_client.execute.side_effect = Exception("DB Error")

    # Should not raise exception but print error
    set_setting("threads", 10)
    mock_client.execute.assert_called_once()
