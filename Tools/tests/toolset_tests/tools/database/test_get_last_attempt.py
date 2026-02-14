# Tools/tests/toolsets/tools/database/test_get_last_attempt.py
import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from Tools.toolsets.tools.database.get_last_attempt import get_last_attempt
from Tools.core.db_client import DBClient, DBResult


class TestGetLastAttempt(unittest.TestCase):
    def setUp(self):
        self.mock_db_client = MagicMock(spec=DBClient)

    def test_fetches_last_attempt_correctly(self):
        # --- Mock Setup ---
        mock_data = ("TargetTable", "CONFIRM", "Reasoning")
        mock_result = DBResult({"results": [mock_data]})
        self.mock_db_client.execute.return_value = mock_result

        # --- Test Execution ---
        result = get_last_attempt(self.mock_db_client, "Table", "Column")

        # --- Assertions ---
        self.assertEqual(result, mock_data)
        self.mock_db_client.execute.assert_called_once()
        params_arg = self.mock_db_client.execute.call_args.args[1]
        self.assertEqual(params_arg, ["Table", "Column"])

    def test_returns_none_when_no_attempt_found(self):
        self.mock_db_client.execute.return_value = DBResult({"results": []})
        result = get_last_attempt(self.mock_db_client, "Table", "Column")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
