# Tools/tests/toolsets/tools/analysis/test_compare_builds.py
import unittest
from unittest.mock import MagicMock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

from toolsets.tools.analysis.compare_builds import compare_builds
from core.db_client import DBClient, DBResult

class TestCompareBuilds(unittest.TestCase):

    def setUp(self):
        self.mock_db_client = MagicMock(spec=DBClient)

    def test_compare_builds_logic(self):
        # --- Mock Data ---
        # Schema for Build A
        schema_A = {
            "tables": [("table_shared",), ("table_removed",)],
            "build_id": 1,
            "table_shared_cols": [("id",), ("name",), ("build_id",)],
            "table_shared_count": 100,
            "table_removed_cols": [("id",), ("value",), ("build_id",)],
            "table_removed_count": 50,
        }
        # Schema for Build B
        schema_B = {
            "tables": [("table_shared",), ("table_added",)],
            "build_id": 2,
            "table_shared_cols": [("id",), ("name_changed",), ("build_id",)],
            "table_shared_count": 110,
            "table_added_cols": [("id",), ("description",), ("build_id",)],
            "table_added_count": 25,
        }

        # --- Mocking Side Effect ---
        def mock_execute_side_effect(sql, params=None):
            # Build ID lookups
            if "registry.builds" in sql and params == ["1.0.0"]:
                return DBResult({"results": [(schema_A["build_id"],)]})
            if "registry.builds" in sql and params == ["2.0.0"]:
                return DBResult({"results": [(schema_B["build_id"],)]})
            
            # Table list lookups (same for both builds in this test)
            if "information_schema.tables" in sql:
                # Return tables based on which build is being queried
                build_id = params[0] if params else None
                if build_id == schema_A["build_id"]:
                     return DBResult({"results": schema_A["tables"]})
                elif build_id == schema_B["build_id"]:
                     return DBResult({"results": schema_B["tables"]})
                else: # Fallback for general table list call
                    all_tables = list(set(schema_A["tables"]) | set(schema_B["tables"]))
                    return DBResult({"results": all_tables})


            # --- Build A Specific Mocks ---
            if params and schema_A["build_id"] in params:
                if 'DESCRIBE archive."table_shared"' in sql:
                    return DBResult({"results": schema_A["table_shared_cols"]})
                if 'COUNT(*) FROM archive."table_shared"' in sql:
                    return DBResult({"results": [(schema_A["table_shared_count"],)]})
                if 'DESCRIBE archive."table_removed"' in sql:
                    return DBResult({"results": schema_A["table_removed_cols"]})
                if 'COUNT(*) FROM archive."table_removed"' in sql:
                    return DBResult({"results": [(schema_A["table_removed_count"],)]})
            
            # --- Build B Specific Mocks ---
            if params and schema_B["build_id"] in params:
                if 'DESCRIBE archive."table_shared"' in sql:
                    return DBResult({"results": schema_B["table_shared_cols"]})
                if 'COUNT(*) FROM archive."table_shared"' in sql:
                    return DBResult({"results": [(schema_B["table_shared_count"],)]})
                if 'DESCRIBE archive."table_added"' in sql:
                    return DBResult({"results": schema_B["table_added_cols"]})
                if 'COUNT(*) FROM archive."table_added"' in sql:
                    return DBResult({"results": [(schema_B["table_added_count"],)]})

            return DBResult({"results": []})

        # This mock needs to be stateful to distinguish calls for build A and B
        call_tracker = {'build_id': None}
        def smart_mock(sql, params=None):
            if "registry.builds" in sql:
                if params == ["1.0.0"]: call_tracker['build_id'] = 1
                if params == ["2.0.0"]: call_tracker['build_id'] = 2
                return DBResult({"results": [(call_tracker['build_id'],)]})

            if "information_schema.tables" in sql:
                return DBResult({"results": [("table_shared",), ("table_removed",),("table_added",)]})

            # Describe calls are generic
            if 'DESCRIBE archive."table_shared"' in sql:
                return DBResult({"results": schema_A["table_shared_cols"] if call_tracker['build_id'] == 1 else schema_B["table_shared_cols"]})
            if 'DESCRIBE archive."table_removed"' in sql:
                return DBResult({"results": schema_A["table_removed_cols"]})
            if 'DESCRIBE archive."table_added"' in sql:
                return DBResult({"results": schema_B["table_added_cols"]})

            # Count calls are specific
            if 'COUNT(*)' in sql:
                build_id_param = params[0]
                if 'table_shared' in sql:
                    count = schema_A["table_shared_count"] if build_id_param == 1 else schema_B["table_shared_count"]
                    return DBResult({"results": [(count,)]})
                if 'table_removed' in sql:
                    count = schema_A["table_removed_count"] if build_id_param == 1 else 0
                    return DBResult({"results": [(count,)]})
                if 'table_added' in sql:
                    count = schema_B["table_added_count"] if build_id_param == 2 else 0
                    return DBResult({"results": [(count,)]})
            
            return DBResult({"results": []})

        self.mock_db_client.execute.side_effect = smart_mock

        # --- Test Execution ---
        diff = compare_builds(self.mock_db_client, "1.0.0", "2.0.0")
        
        # --- Assertions ---
        self.assertEqual(len(diff["added_tables"]), 1)
        self.assertEqual(diff["added_tables"][0]["name"], "table_added")
        self.assertEqual(diff["added_tables"][0]["count"], schema_B["table_added_count"])
        
        self.assertEqual(len(diff["removed_tables"]), 1)
        self.assertEqual(diff["removed_tables"][0]["name"], "table_removed")
        self.assertEqual(diff["removed_tables"][0]["count"], schema_A["table_removed_count"])

        self.assertIn("table_shared", diff["modified_tables"])
        modified_changes = diff["modified_tables"]["table_shared"]
        self.assertIn("Count: 100 -> 110 (+10)", modified_changes)
        self.assertIn("Added columns: name_changed", modified_changes)
        self.assertIn("Removed columns: name", modified_changes)

if __name__ == '__main__':
    unittest.main()
