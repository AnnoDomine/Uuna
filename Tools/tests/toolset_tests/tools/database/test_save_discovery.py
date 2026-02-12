# Tools/tests/toolsets/tools/database/test_save_discovery.py
import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from toolsets.tools.database.save_discovery import save_discovery
from core.db_client import DBClient

class TestSaveDiscovery(unittest.TestCase):

    def setUp(self):
        self.mock_db_client = MagicMock(spec=DBClient)

    def test_saves_data_correctly(self):
        # --- Mock Setup ---
        # The execute method for an INSERT doesn't need a detailed return value
        self.mock_db_client.execute.return_value = None

        # --- Test Data ---
        test_data = {
            "build_id": 123,
            "table_name": "MyTable",
            "column_name": "MyColumn",
            "discovery": "It's a foreign key to OtherTable",
            "confidence": 0.95
        }

        # --- Test Execution ---
        result = save_discovery(self.mock_db_client, **test_data)

        # --- Assertions ---
        self.assertEqual(result["status"], "success")
        
        # Check that execute was called once with the correct parameters
        self.mock_db_client.execute.assert_called_once()
        call_args = self.mock_db_client.execute.call_args
        
        # SQL will be loaded from file, so we check the params
        params_arg = call_args.args[1]
        self.assertEqual(params_arg, list(test_data.values()))

    def test_handles_db_error(self):
        # Configure the mock to raise an exception
        self.mock_db_client.execute.side_effect = Exception("DB Write Error")
        
        result = save_discovery(self.mock_db_client, 1, "t", "c", "d", 0.5)

        # Assert that the function returns an error status
        self.assertEqual(result["status"], "error")
        self.assertIn("DB Write Error", result["message"])

if __name__ == '__main__':
    unittest.main()
