# Tools/tests/toolsets/tools/database/test_find_column_references.py
import unittest
from unittest.mock import patch
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))

from Tools.toolsets.tools.database.find_column_references import find_column_references
from Tools.core.db_client import DBResult


class TestFindColumnReferences(unittest.TestCase):
    def setUp(self):
        self.db_patcher = patch("Tools.toolsets.tools.database.find_column_references.db")
        self.mock_db = self.db_patcher.start()

    def tearDown(self):
        self.db_patcher.stop()

    def test_finds_column_and_sorts_correctly(self):
        # --- Mock Data ---
        # We have 3 tables: one with the column, one without, and one with a different case
        mock_tables = [("spell_effects",), ("item_prices",), ("mount_data",)]

        # Schemas for each table
        schema_spell_effects = [("spellID",), ("effect_type",)]  # Has spellID
        schema_item_prices = [("itemID",), ("price",)]  # Does not have spellID
        schema_mount_data = [("mountID",), ("SpellID",)]  # Has SpellID (different case)

        # Counts for tables that have the column
        count_spell_effects = 1500
        count_mount_data = 250

        # --- Mocking Side Effect ---
        def mock_execute_side_effect(sql, params=None):
            # 1. Return list of all tables
            if "information_schema.tables" in sql:
                return DBResult({"results": mock_tables})

            # 2. Return schemas based on DESCRIBE call
            if 'DESCRIBE archive."spell_effects"' in sql:
                return DBResult({"results": schema_spell_effects})
            if 'DESCRIBE archive."item_prices"' in sql:
                return DBResult({"results": schema_item_prices})
            if 'DESCRIBE archive."mount_data"' in sql:
                return DBResult({"results": schema_mount_data})

            # 3. Return counts for the correct tables
            if 'COUNT(*) FROM archive."spell_effects"' in sql:
                return DBResult({"results": [(count_spell_effects,)]})
            if 'COUNT(*) FROM archive."mount_data"' in sql:
                return DBResult({"results": [(count_mount_data,)]})

            # Fallback for any other query
            return DBResult({"results": []})

        self.mock_db.execute.side_effect = mock_execute_side_effect

        # --- Test Execution ---
        # Search for 'spellID' (should match 'spellID' and 'SpellID' case-insensitively)
        result = find_column_references("spellID")

        # --- Assertions ---
        self.assertEqual(len(result), 2)
        self.assertIn("spell_effects", result)
        self.assertIn("mount_data", result)
        self.assertNotIn("item_prices", result)

        self.assertEqual(result["spell_effects"], count_spell_effects)
        self.assertEqual(result["mount_data"], count_mount_data)

        # Check if the result is sorted by count descending
        result_keys = list(result.keys())
        self.assertEqual(result_keys[0], "spell_effects")
        self.assertEqual(result_keys[1], "mount_data")


if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()
