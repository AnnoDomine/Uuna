# Tools/tests/test_ai_researcher_agent.py
from unittest.mock import MagicMock, patch
from Tools.agents.ai_researcher_agent import process_build


@patch("Tools.agents.ai_researcher_agent.extract_features_for_build")
@patch("Tools.agents.ai_researcher_agent.perform_column_discovery")
@patch("Tools.agents.ai_researcher_agent.perform_column_mapping")
@patch("Tools.agents.ai_researcher_agent.generate_relationship_map")
def test_process_build_flow(mock_gen_map, mock_mapping, mock_discovery, mock_extract):
    # Setup mocks
    mock_db_client = MagicMock()
    mock_ai_client = MagicMock()

    # Mock registry lookup
    mock_db_client.execute.return_value.fetchone.return_value = (1,)  # build_id

    # Mock columns pending analysis
    mock_db_client.execute.return_value.fetchall.return_value = [(1, "Table", "Column", "INT", 0, 100)]

    # Execution
    process_build(mock_db_client, mock_ai_client, "7.3.5.25600", limit=1)

    # Assertions
    mock_extract.assert_called_once()
    mock_discovery.assert_called_once()
    mock_mapping.assert_called_once()
    mock_gen_map.assert_called_once()
