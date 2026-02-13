# Tools/tests/test_feature_extractor.py
import pytest
from unittest.mock import patch, MagicMock
from Tools.analysis.feature_extractor import process_build_features

@patch("Tools.analysis.feature_extractor.DBClient")
@patch("Tools.analysis.feature_extractor.load_query")
def test_process_build_features_flow(mock_load_query, MockDBClient):
    mock_con = MockDBClient.return_value
    # Mock queries to return some strings
    mock_load_query.return_value = "SELECT 1"
    
    # Mock build id
    mock_con.execute.return_value.fetchone.side_effect = [
        (1,), # build_id
        (True,) # table_exists
    ]
    
    # Mock tables list
    mock_con.execute.return_value.fetchall.return_value = [("TableX",)]
    
    # Mock table info df
    import pandas as pd
    mock_df = pd.DataFrame({"name": ["ID", "Name"]})
    mock_con.execute.return_value.df.return_value = mock_df
    
    # Mock row count
    mock_con.execute.return_value.fetchone.side_effect = [
        (1,), # build_id
        (True,), # table_exists
        (100,), # row_count
        ("INT", 0, 10, 50, 1.0) # stats
    ]
    
    # Run
    process_build_features("1.0.0")
    
    # Verify calls
    assert mock_con.execute.call_count >= 5
