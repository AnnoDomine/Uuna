# Tools/tests/toolsets/tools/analysis/test_extract_features.py
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from toolsets.tools.analysis.extract_features import extract_features_for_build
from core.db_client import DBClient, DBResult

class TestExtractFeatures(unittest.TestCase):

    # This is a complex test, so we patch the db_client at the class level
    @patch('core.db_client.DBClient')
    def test_full_extraction_flow(self, MockDBClient):
        # --- Mock Setup ---
        # 1. Instantiate the mock client from the patched class
        mock_db_client = MockDBClient.return_value
        
        # 2. Define the sequence of return values for execute()
        mock_build_id = (123,)
        mock_tables = [("table_one",), ("table_two",)]
        mock_table_exists = (1,)
        mock_row_count = (100,)
        mock_stats = (10, 100, 'a', 'z', 'VARCHAR')
        mock_samples = [('sample1',), ('sample2',)]

        # The df() method needs to be mocked for the PRAGMA call
        mock_df = pd.DataFrame({'name': ['col_a', 'col_b']})

        # Configure the side effects for execute and df
        mock_db_client.execute.return_value = MagicMock(spec=DBResult)
        mock_db_client.execute.return_value.fetchone.side_effect = [
            mock_build_id,
            mock_table_exists, # for table_one
            mock_row_count,  # for table_one
            mock_stats,      # for table_one.col_a
            mock_stats,      # for table_one.col_b
            mock_table_exists, # for table_two
            mock_row_count,  # for table_two
            mock_stats,      # for table_two.col_a
            mock_stats,      # for table_two.col_b
            None # for mark_indexed
        ]
        mock_db_client.execute.return_value.fetchall.side_effect = [
            mock_tables,
            mock_samples, # for table_one.col_a
            mock_samples, # for table_one.col_b
            mock_samples, # for table_two.col_a
            mock_samples, # for table_two.col_b
        ]
        mock_db_client.execute.return_value.df.return_value = mock_df
        
        # --- Test Execution ---
        build_version = "12.0.0"
        result = extract_features_for_build(mock_db_client, build_version)

        # --- Assertions ---
        # 1. Check the summary
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["processed_tables"], 2)
        self.assertEqual(result["processed_columns"], 4) # 2 tables * 2 columns

        # 2. Check if key functions were called.
        # We can check the call count of save_feature to ensure the inner loop ran
        save_feature_call_count = 0
        mark_indexed_call_count = 0
        
        for call in mock_db_client.execute.call_args_list:
            sql = call.args[0]
            if "INSERT INTO research.features" in sql:
                save_feature_call_count += 1
            if "UPDATE registry.builds SET indexed = TRUE" in sql:
                mark_indexed_call_count += 1
        
        self.assertEqual(save_feature_call_count, 4) # 2 tables * 2 columns
        self.assertEqual(mark_indexed_call_count, 1)

if __name__ == '__main__':
    unittest.main()
