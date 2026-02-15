# Tools/tests/toolsets/tools/database/test_get_last_attempt.py
import unittest
from unittest.mock import patch
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from Tools.toolsets.tools.database.get_last_attempt import get_last_attempt
from Tools.core.db_client import DBResult


class TestGetLastAttempt(unittest.TestCase):
    def setUp(self):
        self.db_patcher = patch("Tools.toolsets.tools.database.get_last_attempt.db")
        self.mock_db = self.db_patcher.start()

    def tearDown(self):
        self.db_patcher.stop()

    def test_fetches_last_attempt_correctly(self):
        # --- Mock Setup ---
        mock_data = ("TargetTable", "CONFIRM", "Reasoning")
        mock_result = DBResult({"results": [mock_data]})
        self.mock_db.execute.return_value = mock_result

        # --- Test Execution ---
        result = get_last_attempt("Table", "Column")

        # --- Assertions ---
        self.assertEqual(result, mock_data)
        self.mock_db.execute.assert_called_once()
        params_arg = self.mock_db.execute.call_args.args[1]
        self.assertEqual(params_arg, ["Table", "Column"])

    def test_returns_none_when_no_attempt_found(self):
        self.mock_db.execute.return_value = DBResult({"results": []})
        result = get_last_attempt("Table", "Column")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
