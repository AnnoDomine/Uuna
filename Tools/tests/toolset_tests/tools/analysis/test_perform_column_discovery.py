# Tools/tests/toolset_tests/tools/analysis/test_perform_column_discovery.py
from unittest.mock import MagicMock, patch
from Tools.toolsets.tools.analysis.perform_column_discovery import perform_column_discovery

def test_full_discovery_flow():
    with (
        patch("Tools.toolsets.tools.analysis.perform_column_discovery.save_discovery") as mock_save_discovery,
        patch("Tools.toolsets.tools.analysis.perform_column_discovery.get_last_attempt") as mock_last_attempt,
        patch("Tools.toolsets.tools.analysis.perform_column_discovery.get_wago_structure") as mock_wago,
        patch("Tools.toolsets.tools.analysis.perform_column_discovery.search_wow_wiki") as mock_wiki,
        patch("Tools.toolsets.tools.analysis.perform_column_discovery.fetch_web_content") as mock_fetch,
        patch("Tools.toolsets.tools.analysis.perform_column_discovery.db") as mock_db,
    ):
        # --- Mock Setup ---
        # Sequence for: get_column_samples, get_legacy_discoveries, get_global_knowledge
        mock_db.execute.return_value.fetchall.side_effect = [
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
        result = perform_column_discovery(mock_ai_func, col_info, 123, "10.0.0")

        # --- Assertions ---
        assert result["discovery"] == "Test Result"
        assert result["confidence"] == 0.9

        # Verify that sub-tools and AI were called
        mock_ai_func.assert_called_once()
        mock_save_discovery.assert_called_once()
        mock_wago.assert_called_once()
