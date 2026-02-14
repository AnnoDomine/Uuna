# Tools/tests/toolsets/tools/database/test_get_confirmed_mappings.py
import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from Tools.toolsets.tools.database.get_confirmed_mappings import get_confirmed_mappings
from Tools.core.db_client import DBClient, DBResult


class TestGetConfirmedMappings(unittest.TestCase):
    def setUp(self):
        self.mock_db_client = MagicMock(spec=DBClient)

    def test_fetches_and_returns_mappings(self):
        # --- Mock Data ---
        mock_data = [
            ("spell_effects", "parent_spell_id", "spells"),
            ("item_appearance", "item_id", "items"),
        ]
        mock_result = DBResult({"columns": ["source_table", "column_pattern", "target_table"], "results": mock_data})

        # Configure the mock client to return the mock result
        self.mock_db_client.execute.return_value = mock_result

        # --- Test Data ---
        build_version = "10.0.1"

        # --- Test Execution ---
        result = get_confirmed_mappings(self.mock_db_client, build_version)

        # --- Assertions ---
        # 1. Assert that execute was called once
        self.mock_db_client.execute.assert_called_once()

        # 2. Check the arguments passed to execute (optional but good practice)
        # We can't easily check the SQL content without more work, but we can check the params
        call_args = self.mock_db_client.execute.call_args
        self.assertEqual(call_args.args[1], [build_version])

        # 3. Assert that the result matches the mock data
        self.assertEqual(len(result), 2)
        self.assertEqual(result, mock_data)

    def test_handles_db_error(self):
        # Configure the mock to raise an exception
        self.mock_db_client.execute.side_effect = Exception("DB Connection Error")

        build_version = "10.0.1"
        result = get_confirmed_mappings(self.mock_db_client, build_version)

        # Assert that the function returns an empty list on error
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
