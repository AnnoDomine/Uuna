# Tools/tests/toolsets/tools/database/test_save_attempt.py
import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from Tools.toolsets.tools.database.save_attempt import save_attempt
from Tools.core.db_client import DBClient


class TestSaveAttempt(unittest.TestCase):
    def setUp(self):
        self.mock_db_client = MagicMock(spec=DBClient)

    def test_saves_attempt_correctly(self):
        self.mock_db_client.execute.return_value = None

        test_data = {
            "build_version": "1.2.3",
            "table_name": "TestTable",
            "column_name": "TestColumnID",
            "proposed_target": "TargetTable",
            "decision": "CONFIRM",
            "reasoning": "High confidence match.",
        }

        result = save_attempt(self.mock_db_client, **test_data)

        self.assertEqual(result["status"], "success")

        self.mock_db_client.execute.assert_called_once()
        call_args = self.mock_db_client.execute.call_args
        params_arg = call_args.args[1]
        self.assertEqual(params_arg, list(test_data.values()))


if __name__ == "__main__":
    unittest.main()
