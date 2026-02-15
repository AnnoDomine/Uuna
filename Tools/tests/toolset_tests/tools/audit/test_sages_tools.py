# Tools/tests/toolset_tests/tools/audit/test_sages_tools.py
from unittest.mock import patch
from Tools.toolsets.tools.audit.check_logical_consistency import check_logical_consistency
from Tools.toolsets.tools.audit.grant_final_verdict import grant_final_verdict


def test_check_logical_consistency_no_conflict():
    with patch("Tools.toolsets.tools.audit.check_logical_consistency.db") as mock_db:
        # Mock return for: column_pattern, source_table, target_table, confidence, notes
        mock_db.execute.return_value.fetchall.return_value = [("QuestID", "TableX", "Quests", 0.9, "Legacy mapping")]

        result = check_logical_consistency("TableX", "QuestID", "Quests")

        assert result["status"] == "consistent"


def test_check_logical_consistency_with_conflict():
    with patch("Tools.toolsets.tools.audit.check_logical_consistency.db") as mock_db:
        mock_db.execute.return_value.fetchall.return_value = [("QuestID", "TableX", "Quests", 0.9, "Legacy mapping")]

        result = check_logical_consistency("TableX", "QuestID", "Items")  # WRONG TARGET

        assert result["status"] == "contradictory"
        assert len(result["conflicts"]) == 1
        assert result["conflicts"][0]["existing_target"] == "Quests"


def test_grant_final_verdict_approve():
    with patch("Tools.toolsets.tools.audit.grant_final_verdict.db") as mock_db:
        result = grant_final_verdict("tk-1", "APPROVE", "Found everything")

        assert result["status"] == "success"
        assert result["new_task_status"] == "pending_librarian"
        mock_db.execute.assert_called_once()


def test_grant_final_verdict_block():
    with patch("Tools.toolsets.tools.audit.grant_final_verdict.db"):
        result = grant_final_verdict("tk-1", "BLOCK", "Lacking proof")

        assert result["status"] == "success"
        assert result["new_task_status"] == "rejected"
