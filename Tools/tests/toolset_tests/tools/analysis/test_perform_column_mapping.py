# Tools/tests/toolset_tests/tools/analysis/test_perform_column_mapping.py
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add Tools to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

pcm_module = sys.modules['toolsets.tools.analysis.perform_column_mapping']
from toolsets.tools.analysis.perform_column_mapping import perform_column_mapping
from core.db_client import DBResult

class TestPerformColumnMapping(unittest.TestCase):

    def test_full_mapping_confirmed(self):
        with patch.object(pcm_module, 'check_ids') as mock_check_ids, \
             patch.object(pcm_module, 'save_attempt') as mock_save_attempt, \
             patch.object(pcm_module, 'update_global_knowledge') as mock_update, \
             patch('core.db_client.DBClient') as MockDBClient:
            
            # --- Mock Setup ---
            mock_db_client = MockDBClient.return_value
            mock_db_client.execute.return_value = MagicMock(spec=DBResult)
            
            # Responses for get_statistical_predictions and get_available_tables
            mock_db_client.execute.return_value.fetchall.side_effect = [
                [("Prediction",)], # preds
                [("TargetTable",), ("OtherTable",)] # all_tables
            ]

            # AI mock for Engineer and then Critic
            mock_ai_func = MagicMock()
            mock_ai_func.side_effect = [
                {"target": "TargetTable", "confidence": 0.9, "reasoning": "Good match"}, # Engineer
                {"decision": "confirm", "reasoning": "IDs exist"} # Critic
            ]

            mock_check_ids.return_value = 10
            mock_save_attempt.return_value = {"status": "success"}
            mock_update.return_value = {"status": "success"}

            # --- Test Execution ---
            discovery_res = {"ai_full_response": {"type": "structure"}}
            col_info = [1, "Table", "Column", "INT", 0, 100]
            result = perform_column_mapping(
                mock_db_client, mock_ai_func, discovery_res, col_info, "10.0.0", 
                samples=[1, 2, 3], memory_section="M", online_info="O"
            )

            # --- Assertions ---
            assert result["status"] == "confirmed"
            assert result["target"] == "TargetTable"
            assert result["mapping_confirmed"]
            
            # Verify calls
            assert mock_ai_func.call_count == 2
            mock_check_ids.assert_called_once()
            mock_save_attempt.assert_called_once()
            mock_update.assert_called_once()

    def test_skips_non_mapping_candidate(self):
        with patch('core.db_client.DBClient') as MockDBClient:
            mock_db_client = MockDBClient.return_value
            mock_db_client.execute.return_value = MagicMock(spec=DBResult)
            mock_db_client.execute.return_value.fetchall.return_value = [] # no predictions

            discovery_res = {"ai_full_response": {"type": "value"}} # Not a structure
            col_info = [1, "Table", "msec_column", "INT", 0, 100]
            
            mock_ai_func = MagicMock()
            result = perform_column_mapping(mock_db_client, mock_ai_func, discovery_res, col_info, "10.0.0")

            assert result["status"] == "skipped"
            mock_ai_func.assert_not_called()

if __name__ == '__main__':
    unittest.main()
