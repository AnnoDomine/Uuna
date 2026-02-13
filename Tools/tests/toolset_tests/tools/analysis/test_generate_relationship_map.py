# Tools/tests/toolset_tests/tools/analysis/test_generate_relationship_map.py
import unittest
from unittest.mock import MagicMock, patch
from toolsets.tools.analysis.generate_relationship_map import generate_relationship_map
from core.db_client import DBResult

import toolsets.tools.analysis.generate_relationship_map
import sys
grm_module = sys.modules["toolsets.tools.analysis.generate_relationship_map"]


class TestGenerateRelationshipMap(unittest.TestCase):
    def test_orchestration_flow(self):
        with (
            patch.object(grm_module, "get_confirmed_mappings") as mock_get_mappings,
            patch.object(grm_module, "save_mermaid_diagram") as mock_save_diagram,
            patch("core.db_client.DBClient") as MockDBClient,
        ):
            # --- Mock Setup ---
            mock_db_client = MockDBClient.return_value
            # Simulate cache miss for mermaid docs
            mock_db_client.execute.return_value = DBResult({"results": []})

            # 2. Mock the AI function
            mock_ai_response = {"mermaid": "erDiagram\nFAKE_DATA", "description": "A fake diagram"}
            mock_ask_ai_func = MagicMock(return_value=mock_ai_response)

            # 3. Configure the patched tool mocks
            mock_mappings_data = [("table1", "col1", "table2")]
            mock_get_mappings.return_value = mock_mappings_data

            mock_save_status = "SUCCESS: Diagram saved to Data/maps/Build_Map_11.0.0.mmd"
            mock_save_diagram.return_value = mock_save_status

            # --- Test Data ---
            build_version = "11.0.0"

            # --- Test Execution ---
            result = generate_relationship_map(mock_db_client, mock_ask_ai_func, build_version)

            # --- Assertions ---
            # Assert that the dependent tools were called correctly
            mock_get_mappings.assert_called_once_with(mock_db_client, build_version)
            mock_ask_ai_func.assert_called_once()

            # Assert that the save function was called with the mermaid code from the AI
            mock_save_diagram.assert_called_once_with(
                name="Build_Map", content=mock_ai_response["mermaid"], build_version=build_version
            )

            # Assert that the final status is the one returned by the save function
            assert result == mock_save_status

    def test_no_mappings_found(self):
        with patch.object(grm_module, "get_confirmed_mappings", return_value=[]):
            mock_db_client = MagicMock()
            mock_ask_ai_func = MagicMock()

            result = generate_relationship_map(mock_db_client, mock_ask_ai_func, "11.0.0")

            # Assert no AI call or save was attempted
            mock_ask_ai_func.assert_not_called()
            assert result.startswith("INFO: No confirmed mappings found")


if __name__ == "__main__":
    unittest.main()
