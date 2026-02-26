# Tools/tests/toolset_tests/tools/analysis/test_compare_builds.py
from unittest.mock import MagicMock, patch
from Tools.toolsets.tools.analysis.compare_builds import compare_builds

def test_compare_builds_logic():
    # --- Mock Data ---
    schema_A = {
        "tables": [("table_shared",), ("table_removed",)],
        "build_id": 1,
        "table_shared_cols": [("id",), ("name",), ("build_id",)],
        "table_shared_count": 100,
        "table_removed_cols": [("id",), ("value",), ("build_id",)],
        "table_removed_count": 50,
    }
    schema_B = {
        "tables": [("table_shared",), ("table_added",)],
        "build_id": 2,
        "table_shared_cols": [("id",), ("name_changed",), ("build_id",)],
        "table_shared_count": 110,
        "table_added_cols": [("id",), ("description",), ("build_id",)],
        "table_added_count": 25,
    }

    with patch("Tools.toolsets.tools.analysis.compare_builds.db") as mock_db:
        describe_counter = {"table_shared": 0}

        def descriptive_mock(sql, params=None):
            # 1. Build ID lookup
            if "FROM registry.builds" in sql:
                if params == ["1.0.0"]:
                    return MagicMock(fetchone=lambda: (1,))
                if params == ["2.0.0"]:
                    return MagicMock(fetchone=lambda: (2,))
            
            # 2. Table list
            if "information_schema.tables" in sql:
                return MagicMock(fetchall=lambda: [("table_shared",), ("table_removed",), ("table_added",)])
            
            # 3. Describe calls
            if "DESCRIBE archive" in sql:
                if "table_shared" in sql:
                    res = schema_A["table_shared_cols"] if describe_counter["table_shared"] == 0 else schema_B["table_shared_cols"]
                    describe_counter["table_shared"] += 1
                    return MagicMock(fetchall=lambda: res)
                if "table_removed" in sql:
                    return MagicMock(fetchall=lambda: schema_A["table_removed_cols"])
                if "table_added" in sql:
                    return MagicMock(fetchall=lambda: schema_B["table_added_cols"])
            
            # 4. Count calls
            if "COUNT(*)" in sql:
                bid = params[0]
                if "table_shared" in sql:
                    return MagicMock(fetchone=lambda: (100 if bid == 1 else 110,))
                if "table_removed" in sql:
                    return MagicMock(fetchone=lambda: (50 if bid == 1 else 0,))
                if "table_added" in sql:
                    return MagicMock(fetchone=lambda: (0 if bid == 1 else 25,))
            
            return MagicMock(fetchall=lambda: [], fetchone=lambda: (0,))

        mock_db.execute.side_effect = descriptive_mock

        diff = compare_builds("1.0.0", "2.0.0")

        # --- Assertions ---
        assert len(diff["added_tables"]) == 1
        assert diff["added_tables"][0]["name"] == "table_added"
        assert len(diff["removed_tables"]) == 1
        assert diff["removed_tables"][0]["name"] == "table_removed"
        assert "table_shared" in diff["modified_tables"]
        
        mods = diff["modified_tables"]["table_shared"]
        assert any("Count: 100 -> 110" in m for m in mods)
        assert any("Added columns: name_changed" in m for m in mods)
        assert any("Removed columns: name" in m for m in mods)
