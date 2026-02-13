# Tools/tests/toolset_tests/tools/analysis/test_run_mass_indexing.py
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add Tools to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

rmi_module = sys.modules["toolsets.tools.analysis.run_mass_indexing"]
from toolsets.tools.analysis.run_mass_indexing import run_mass_indexing
from core.db_client import DBResult


class TestRunMassIndexing(unittest.TestCase):
    def test_indexing_flow(self):
        with (
            patch.object(rmi_module, "extract_features_for_build") as mock_extract_features,
            patch("core.db_client.DBClient") as MockDBClient,
        ):
            # --- Mock Setup ---
            mock_db_client = MockDBClient.return_value

            all_versions = [("1.0",), ("1.1",), ("1.2",), ("1.3",)]
            pending_builds = [("1.1",), ("1.3",)]

            def execute_side_effect(sql, params=None):
                mock_result = MagicMock(spec=DBResult)
                # Check for unique substrings from the actual SQL content
                if "indexed = FALSE" in sql:  # Unique to get_pending_builds.sql
                    mock_result.fetchall.return_value = pending_builds
                elif "ORDER BY id ASC" in sql:  # For get_all_versions.sql
                    mock_result.fetchall.return_value = all_versions
                else:
                    mock_result.fetchall.return_value = []
                return mock_result

            mock_db_client.execute.side_effect = execute_side_effect

            # Mock the tool we are calling
            mock_extract_features.return_value = {"status": "success"}

            # --- Test Execution ---
            # No range, should process all pending
            result = run_mass_indexing(mock_db_client)

            # --- Assertions ---
            assert result["processed_successfully"] == 2
            assert len(result["failed_builds"]) == 0

            # Check that extract_features was called for the correct builds
            assert mock_extract_features.call_count == 2
            mock_extract_features.assert_any_call(mock_db_client, "1.1")
            mock_extract_features.assert_any_call(mock_db_client, "1.3")

    def test_indexing_with_range(self):
        with (
            patch.object(rmi_module, "extract_features_for_build") as mock_extract_features,
            patch("core.db_client.DBClient") as MockDBClient,
        ):
            # --- Mock Setup ---
            mock_db_client = MockDBClient.return_value
            all_versions = [("1.0",), ("1.1",), ("1.2",), ("1.3",)]
            pending_builds = [("1.1",), ("1.3",)]

            def execute_side_effect(sql, params=None):
                mock_result = MagicMock(spec=DBResult)
                # Check for unique substrings from the actual SQL content
                if "indexed = FALSE" in sql:  # Unique to get_pending_builds.sql
                    mock_result.fetchall.return_value = pending_builds
                elif "ORDER BY id ASC" in sql:  # For get_all_versions.sql
                    mock_result.fetchall.return_value = all_versions
                else:
                    mock_result.fetchall.return_value = []
                return mock_result

            mock_db_client.execute.side_effect = execute_side_effect

            mock_extract_features.return_value = {"status": "success"}

            # --- Test Execution ---
            # Range includes 1.1 but excludes 1.3
            result = run_mass_indexing(mock_db_client, start_v="1.0", end_v="1.2")

            # --- Assertions ---
            assert result["processed_successfully"] == 1
            # Check that extract_features was called only for build 1.1
            assert mock_extract_features.call_count == 1
            mock_extract_features.assert_called_once_with(mock_db_client, "1.1")


if __name__ == "__main__":
    unittest.main()
