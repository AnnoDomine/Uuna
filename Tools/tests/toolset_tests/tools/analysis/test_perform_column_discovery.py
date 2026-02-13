# Tools/tests/toolset_tests/tools/analysis/test_perform_column_discovery.py
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add Tools to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

# Import to ensure it's in sys.modules
pcd_module = sys.modules["toolsets.tools.analysis.perform_column_discovery"]
from toolsets.tools.analysis.perform_column_discovery import perform_column_discovery
from core.db_client import DBResult


class TestPerformColumnDiscovery(unittest.TestCase):
    def test_full_discovery_flow(self):
        with (
            patch.object(pcd_module, "save_discovery") as mock_save_discovery,
            patch.object(pcd_module, "get_last_attempt") as mock_last_attempt,
            patch.object(pcd_module, "get_wago_structure") as mock_wago,
            patch.object(pcd_module, "search_wow_wiki") as mock_wiki,
            patch.object(pcd_module, "fetch_web_content") as mock_fetch,
            patch("core.db_client.DBClient") as MockDBClient,
        ):
            # --- Mock Setup ---
            mock_db_client = MockDBClient.return_value
            mock_db_client.execute.return_value = MagicMock(spec=DBResult)

            # Sequence for: get_column_samples, get_legacy_discoveries, get_global_knowledge
            mock_db_client.execute.return_value.fetchall.side_effect = [
                [(10,), (20,)],  # samples
                [("Prev Discovery",)],  # legacy
                [],  # existing knowledge
            ]

            mock_last_attempt.return_value = None
            mock_wago.return_value = "WAGO_DATA"
            mock_wiki.return_value = ["URL"]
            mock_fetch.return_value = "WIKI_CONTENT"

            mock_ai_func = MagicMock(return_value={"discovery": "Test Result", "confidence": 0.9})
            mock_save_discovery.return_value = {"status": "success"}

            # --- Test Execution ---
            # col_info: f_id, table, col, d_type, v_min, v_max
            col_info = [1, "Table", "Column", "INT", 0, 100]
            result = perform_column_discovery(mock_db_client, mock_ai_func, col_info, 123, "10.0.0")

            # --- Assertions ---
            assert result["discovery"] == "Test Result"
            assert result["confidence"] == 0.9

            # Verify that sub-tools and AI were called
            mock_ai_func.assert_called_once()
            mock_save_discovery.assert_called_once()
            mock_wago.assert_called_once()


if __name__ == "__main__":
    unittest.main()
