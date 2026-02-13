# Tools/tests/test_sync_wow_db.py
import duckdb
from unittest.mock import patch, MagicMock
from Tools.ingestion.sync_wow_db import sync_build

def test_sync_build_flow(tmp_path, monkeypatch):
    db_path = str(tmp_path / "test_master.duckdb")
    con = duckdb.connect(db_path)
    con.execute("CREATE SCHEMA registry")
    con.execute("CREATE TABLE registry.builds (id INTEGER, version TEXT, product TEXT, is_downloaded BOOLEAN)")
    con.close()

    monkeypatch.setattr("Tools.ingestion.sync_wow_db.MASTER_DB", db_path)
    
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
        
        sync_build("1.0.0.123")
        
        # Verify build was added to registry
        con = duckdb.connect(db_path)
        row = con.execute("SELECT version FROM registry.builds").fetchone()
        assert row == ("1.0.0.123",)
        con.close()
        
        # Verify master_ingester was called
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        assert "master_ingester.py" in args[0][1]
