# Tools/tests/toolsets/tools/database/test_check_ids.py
import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from toolsets.tools.database.check_ids import check_ids
from core.db_client import DBClient, DBResult

class TestCheckIds(unittest.TestCase):

    def setUp(self):
        self.mock_db_client = MagicMock(spec=DBClient)

    def test_checks_valid_ids(self):
        # --- Mock Setup ---
        # Simulate that 2 of the 3 provided IDs were found
        mock_result = DBResult({"results": [(2,)]})
        self.mock_db_client.execute.return_value = mock_result
        
        # --- Test Data ---
        table_name = "ItemSparse"
        id_list = [123, 456, 789, "not-an-id", 0]
        
        # --- Test Execution ---
        count = check_ids(self.mock_db_client, table_name, id_list)

        # --- Assertions ---
        self.assertEqual(count, 2)
        
        # Check that execute was called with the correct parameters
        self.mock_db_client.execute.assert_called_once()
        call_args = self.mock_db_client.execute.call_args
        
        # Check the formatted SQL
        sql_arg = call_args.args[0]
        self.assertIn(f'FROM archive."{table_name}"', sql_arg)
        # 4 valid IDs (123, 456, 789, 0) should result in 4 placeholders
        self.assertEqual(sql_arg.count('?'), 4)
        
        # Check the parameters passed
        params_arg = call_args.args[1]
        self.assertIn(123, params_arg)
        self.assertIn(456, params_arg)
        self.assertIn(789, params_arg)
        self.assertIn(0, params_arg)
        self.assertNotIn("not-an-id", params_arg)

    def test_returns_zero_for_empty_list(self):
        count = check_ids(self.mock_db_client, "some_table", [])
        self.assertEqual(count, 0)
        # Ensure the DB was not hit
        self.mock_db_client.execute.assert_not_called()
        
    def test_handles_invalid_table_name(self):
        with self.assertRaises(ValueError):
            check_ids(self.mock_db_client, "table; DROP TABLE users;", [1, 2])
        self.mock_db_client.execute.assert_not_called()

if __name__ == '__main__':
    unittest.main()
