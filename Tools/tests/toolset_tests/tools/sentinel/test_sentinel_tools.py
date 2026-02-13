# Tools/tests/toolset_tests/tools/sentinel/test_sentinel_tools.py
from Tools.toolsets.tools.sentinel.sanitize_data import sanitize_data
from Tools.toolsets.tools.sentinel.sql_security_audit import sql_security_audit
from Tools.toolsets.tools.sentinel.privacy_protection import privacy_protection


def test_sanitize_data_technical_cleaning():
    html = "<html><body><script>alert(1)</script><div>Lore</div><style>body{}</style></body></html>"
    result = sanitize_data(html)

    assert "Lore" in result["sanitized_content"]
    assert "script" not in result["sanitized_content"]
    assert "style" not in result["sanitized_content"]
    assert result["removed_elements_count"] >= 2


def test_sql_security_audit_blocks_destructive():
    sql = "DROP TABLE registry.builds;"
    result = sql_security_audit(sql)

    assert result["audit_passed"] is False
    assert "DROP" in result["forbidden_detected"]
    assert result["threat_level"] == "Critical"


def test_sql_security_audit_allows_safe():
    sql = "SELECT * FROM archive.Spell WHERE ID = 1;"
    result = sql_security_audit(sql)

    assert result["audit_passed"] is True
    assert result["threat_level"] == "Low"


def test_privacy_protection_masks_secrets():
    content = "My API_KEY is sk_live_1234567890abcdef"
    result = privacy_protection(content)

    assert "sk_live" not in result["protected_data"]
    assert "[MASKED_API KEY]" in result["protected_data"]
    assert result["leaks_detected"] == 1
