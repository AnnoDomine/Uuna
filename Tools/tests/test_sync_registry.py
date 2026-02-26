# Tools/tests/test_sync_registry.py
import duckdb
from Tools.core.sync_registry import sync_registry


def test_sync_registry_flow(tmp_path, monkeypatch):
    # Setup mock DB
    db_path = str(tmp_path / "test_master.duckdb")
    con = duckdb.connect(db_path)
    con.execute("CREATE SCHEMA registry")
    con.execute("CREATE SCHEMA archive")
    con.execute("""
        CREATE TABLE registry.builds (
            id INTEGER PRIMARY KEY,
            version TEXT,
            is_downloaded INTEGER DEFAULT 0,
            indexed INTEGER DEFAULT 0
        )
    """)
    con.execute("INSERT INTO registry.builds (id, version) VALUES (1, '1.0.0'), (2, '2.0.0')")
    con.execute("CREATE TABLE archive.build_data_map (build_id INTEGER, table_name TEXT)")
    con.execute("INSERT INTO archive.build_data_map VALUES (1, 'TableX')")
    con.close()

    # Mock DB_PATH in sync_registry
    monkeypatch.setattr("Tools.core.sync_registry.DB_PATH", db_path)

    # We also need to mock the QUERIES_DIR or ensure it exists
    # For now, let's assume it works because the queries are in the repo

    sync_registry()

    # Verify results
    con = duckdb.connect(db_path)
    stats = con.execute("SELECT is_downloaded, indexed FROM registry.builds WHERE id = 1").fetchone()
    # sync_registry only updates is_downloaded based on build_data_map
    assert stats == (1, 0)

    stats2 = con.execute("SELECT is_downloaded FROM registry.builds WHERE id = 2").fetchone()
    assert stats2 == (0,)
    con.close()
