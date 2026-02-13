# Tools/tests/toolset_tests/tools/system/test_get_my_skills.py
from Tools.toolsets.tools.system.get_my_skills import get_my_skills


def test_get_my_skills_success():
    result = get_my_skills("Archivist")

    assert "role" in result
    assert result["role"] == "Archivist"
    assert "master_skills_content" in result
    assert "column_discovery" in result["available_tasks"]


def test_get_my_skills_not_found():
    result = get_my_skills("NonExistentAgent")

    assert "error" in result
    assert result["role"] == "NonExistentAgent"
