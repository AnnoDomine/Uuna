# Tools/tests/toolsets/tools/database/test_update_global_knowledge.py
import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from toolsets.tools.database.update_global_knowledge import update_global_knowledge
from core.db_client import DBClient


class TestUpdateGlobalKnowledge(unittest.TestCase):
    def setUp(self):
        self.mock_db_client = MagicMock(spec=DBClient)

    def test_updates_knowledge_correctly(self):
        self.mock_db_client.execute.return_value = None

        test_data = {
            "column_pattern": "MyColumnID",
            "source_table": "SourceTable",
            "target_table": "TargetTable",
            "confidence": 0.9,
            "ai_notes": "Note",
            "build_version": "1.2.3",
        }

        result = update_global_knowledge(self.mock_db_client, **test_data)

        self.assertEqual(result["status"], "success")
        self.mock_db_client.execute.assert_called_once()
        params_arg = self.mock_db_client.execute.call_args.args[1]
        self.assertEqual(params_arg, list(test_data.values()))


if __name__ == "__main__":
    unittest.main()
