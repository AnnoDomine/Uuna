# Tools/tests/toolsets/tools/database/test_find_value.py
import unittest
from unittest.mock import patch
import sys
import os

# Ensure the parent directory is in the Python path for module resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from Tools.toolsets.tools.database.find_value import find_value
from Tools.core.db_client import DBResult


class TestFindValue(unittest.TestCase):
    def setUp(self):
        """Set up a mock DBClient before each test."""
        self.db_patcher = patch("Tools.toolsets.tools.database.find_value.db")
        self.mock_db = self.db_patcher.start()

    def tearDown(self):
        self.db_patcher.stop()

    def test_finds_value_in_one_table(self):
        """
        Tests if the tool correctly finds a value in a single table
        and returns the correct count.
        """
        # --- Mock Setup ---
        # 1. Mock the response for getting all tables
        mock_tables_result = DBResult({"columns": ["table_name"], "results": [("item_effects",), ("spell_names",)]})

        # 2. Mock the response for DESCRIBE on the first table 'item_effects'
        mock_describe_item_effects = DBResult(
            {
                "columns": ["column_name", "column_type", "null", "key", "default", "extra"],
                "results": [
                    ("id", "INTEGER", "NO", "PRI", None, None),
                    ("description", "VARCHAR", "YES", "", None, None),
                ],
            }
        )

        # 3. Mock the response for the COUNT query on 'item_effects'
        mock_count_item_effects = DBResult(
            {
                "columns": ["count(*)"],
                "results": [(3,)],  # Simulate 3 matches found
            }
        )

        # 4. Mock the response for DESCRIBE on the second table 'spell_names'
        mock_describe_spell_names = DBResult(
            {
                "columns": ["column_name", "column_type", "null", "key", "default", "extra"],
                "results": [("id", "INTEGER", "NO", "PRI", None, None), ("name", "VARCHAR", "YES", "", None, None)],
            }
        )

        # 5. Mock the response for the COUNT query on 'spell_names'
        mock_count_spell_names = DBResult(
            {
                "columns": ["count(*)"],
                "results": [(0,)],  # Simulate 0 matches found
            }
        )

        # Configure the side_effect to return different mocks based on the query
        def mock_execute_side_effect(sql, params=None):
            if "information_schema.tables" in sql:
                return mock_tables_result
            elif 'DESCRIBE archive."item_effects"' in sql:
                return mock_describe_item_effects
            elif 'COUNT(*) FROM archive."item_effects"' in sql:
                return mock_count_item_effects
            elif 'DESCRIBE archive."spell_names"' in sql:
                return mock_describe_spell_names
            elif 'COUNT(*) FROM archive."spell_names"' in sql:
                return mock_count_spell_names
            return DBResult({"results": [], "columns": []})

        self.mock_db.execute.side_effect = mock_execute_side_effect

        # --- Test Execution ---
        search_term = "Frostbolt"
        result = find_value(search_term)

        # --- Assertions ---
        self.assertIn("item_effects", result)
        self.assertEqual(result["item_effects"], 3)
        self.assertNotIn("spell_names", result, "Should not include tables with zero matches")
        self.assertEqual(len(result), 1)

    def test_with_build_version_filter(self):
        """
        Tests if the tool correctly applies a build version filter.
        """
        # --- Mock Setup ---
        mock_build_id_result = DBResult({"columns": ["id"], "results": [(123,)]})
        mock_tables_result = DBResult({"columns": ["table_name"], "results": [("item_effects",)]})
        # Note: Added 'build_id' to the columns
        mock_describe_result = DBResult(
            {
                "columns": ["column_name", "column_type", "null", "key", "default", "extra"],
                "results": [("id", "INTEGER", "NO", "PRI", None, None), ("build_id", "INTEGER", "YES", "", None, None)],
            }
        )
        mock_count_result = DBResult({"columns": ["count(*)"], "results": [(1,)]})

        def mock_execute_side_effect(sql, params=None):
            if "registry.builds" in sql:
                self.assertEqual(params, ["10.2.5.52762"])
                return mock_build_id_result
            if "information_schema.tables" in sql:
                return mock_tables_result
            if "DESCRIBE" in sql:
                return mock_describe_result
            if "COUNT(*)" in sql:
                # Check if the build_id was correctly added to the query params
                self.assertIn(123, params)
                return mock_count_result
            return DBResult({"results": [], "columns": []})

        self.mock_db.execute.side_effect = mock_execute_side_effect

        # --- Test Execution ---
        result = find_value("TestValue", build_version="10.2.5.52762")

        # --- Assertions ---
        self.assertIn("item_effects", result)
        self.assertEqual(result["item_effects"], 1)


if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()
