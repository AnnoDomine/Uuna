# Tools/tests/toolset_tests/tools/analysis/test_map_column_references_workflow.py
from unittest.mock import MagicMock, patch
from Tools.toolsets.tools.analysis.map_column_references_workflow import map_column_references_workflow

def test_workflow_with_high_and_low_confidence():
    with (
        patch("Tools.toolsets.tools.analysis.map_column_references_workflow._load_json") as mock_load_json,
        patch("Tools.toolsets.tools.analysis.map_column_references_workflow._save_json") as mock_save_json,
        patch("Tools.toolsets.tools.analysis.map_column_references_workflow.guess_table_reference") as mock_guess,
        patch("Tools.toolsets.tools.analysis.map_column_references_workflow.db") as mock_db,
    ):
        # --- Mock Setup ---
        all_tables_mock = [("ItemSparse",), ("SomeOtherTable",)]
        itemsparse_cols_mock = [("CharacterID",), ("QuestID",)]
        other_cols_mock = [("SomeColumn",)]

        def db_execute_side_effect(sql, params=None):
            mock_result = MagicMock()
            if "information_schema.tables" in sql:
                mock_result.fetchall.return_value = all_tables_mock
            elif "get_table_columns" in sql or "PRAGMA" in sql:
                if "ItemSparse" in sql:
                    mock_result.fetchall.return_value = itemsparse_cols_mock
                else:
                    mock_result.fetchall.return_value = other_cols_mock
            elif "count_active_entries" in sql or "COUNT" in sql:
                mock_result.fetchone.return_value = (100,)
            else:  # Default for other queries like get_previous_build
                mock_result.fetchone.return_value = None
                mock_result.fetchall.return_value = []
            return mock_result

        mock_db.execute.side_effect = db_execute_side_effect

        # 2. Mock JSON loading
        mock_load_json.return_value = {}

        # 3. Mock the guesser tool's side effect
        def guess_side_effect(potential_name, all_tables):
            if potential_name == "Character":  # Low confidence
                return [{"table": "CharacterFacialHairStyles", "reason": "Fuzzy Match", "confidence": 0.7}]
            if potential_name == "Quest":  # High confidence
                return [{"table": "QuestV2", "reason": "Alias Match", "confidence": 0.98}]
            return []

        mock_guess.side_effect = guess_side_effect

        # --- Test Execution ---
        result = map_column_references_workflow("1.2.3")

        # --- Assertions ---
        assert result["status"] == "complete_with_pending"
        assert result["newly_confirmed_mappings"] == 1
        assert len(result["pending_questions"]) == 1

        pending_q = result["pending_questions"][0]
        assert pending_q["mapping_key"] == "ItemSparse.CharacterID"

        # Get the data that was passed to the first call of _save_json (for user_mappings)
        saved_user_map_data = mock_save_json.call_args_list[0].args[1]
        assert "ItemSparse.QuestID" in saved_user_map_data
        assert saved_user_map_data["ItemSparse.QuestID"] == "QuestV2"
