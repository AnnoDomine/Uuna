# Tools/tests/test_update_build_registry.py
import responses
import duckdb
from Tools.ingestion.update_build_registry import fetch_versions, update_registry


@responses.activate
def test_fetch_versions_success():
    mock_data = {"wow": [{"version": "1.0.0.123"}]}
    responses.add(responses.GET, "https://wago.tools/api/builds", json=mock_data, status=200)

    result = fetch_versions()
    assert result == mock_data


def test_update_registry_flow(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test_master.duckdb")
    con = duckdb.connect(db_path)
    con.execute("CREATE SCHEMA registry")
    con.execute("""
        CREATE TABLE registry.builds (
            id INTEGER,
            version TEXT PRIMARY KEY,
            product TEXT,
            last_seen TIMESTAMP
        )
    """)
    con.close()

    monkeypatch.setattr("Tools.ingestion.update_build_registry.MASTER_DB", db_path)

    mock_data = {"wow": [{"version": "1.0.0.123"}]}
    update_registry(mock_data)

    con = duckdb.connect(db_path)
    row = con.execute("SELECT id, version, product FROM registry.builds").fetchone()
    assert row == (123, "1.0.0.123", "wow")
    con.close()
