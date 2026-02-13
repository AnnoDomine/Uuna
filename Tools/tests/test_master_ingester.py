# Tools/tests/test_master_ingester.py
import pytest
import responses
import os
from unittest.mock import patch, MagicMock
from Tools.ingestion.master_ingester import fetch_tables_for_build, process_table_master

@responses.activate
def test_fetch_tables_api_success():
    version = "1.0.0"
    mock_tables = ["Table1", "Table2"]
    responses.add(responses.GET, f"https://wago.tools/api/db2?build={version}", json=mock_tables, status=200)
    
    result = fetch_tables_for_build(version)
    assert result == mock_tables

@responses.activate
def test_fetch_tables_html_fallback(base_logger_mock):
    version = "1.0.0"
    # Mock API failure
    responses.add(responses.GET, f"https://wago.tools/api/db2?build={version}", status=404)
    # Mock HTML success
    html_content = '<html><body><div data-page="{&quot;props&quot;:{&quot;tables&quot;:[&quot;TableX&quot;]}}"></div></body></html>'
    responses.add(responses.GET, f"https://wago.tools/db2?build={version}", body=html_content, status=200)
    
    result = fetch_tables_for_build(version)
    assert result == ["TableX"]

@pytest.fixture
def base_logger_mock():
    with patch("Tools.ingestion.master_ingester.base_logger") as mock:
        yield mock

@patch("Tools.ingestion.master_ingester.DBClient")
@patch("Tools.ingestion.master_ingester.load_query")
@responses.activate
def test_process_table_master_success(mock_load_query, MockDBClient, tmp_path, monkeypatch):
    # Setup
    monkeypatch.setattr("Tools.ingestion.master_ingester.CSV_TEMP_DIR", str(tmp_path))
    mock_con = MockDBClient.return_value
    mock_load_query.return_value = "SELECT 1"
    
    table = "TestTable"
    version = "1.0.0"
    build_id = 1
    
    # Mock CSV download
    csv_content = b"ID,Name\n1,Test"
    responses.add(responses.GET, f"https://wago.tools/db2/{table}/csv?build={version}", body=csv_content, status=200)
    
    # Mock DB operations
    import pandas as pd
    mock_df = pd.DataFrame({"name": ["ID", "Name"]})
    mock_con.execute.return_value.df.return_value = mock_df
    
    # Run
    result = process_table_master(table, version, build_id)
    
    assert result is True
    assert mock_con.execute.call_count >= 3
