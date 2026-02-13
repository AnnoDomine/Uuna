# Tools/tests/toolset_tests/tools/research/test_vector_and_discoveries.py
import responses
from unittest.mock import MagicMock
from Tools.toolsets.tools.research.query_vector_memory import query_vector_memory
from Tools.toolsets.tools.research.search_discoveries import search_discoveries

@responses.activate
def test_query_vector_memory_success():
    # Setup mock API response
    mock_results = [{"id": "1", "score": 0.9, "content": "Azeroth lore"}]
    responses.add(
        responses.POST, 
        "http://127.0.0.1:8001/memory/search", 
        json={"results": mock_results}, 
        status=200
    )
    
    result = query_vector_memory("Archivist", "Where is Azeroth?")
    
    assert len(result) == 1
    assert result[0]["content"] == "Azeroth lore"

def test_search_discoveries_success():
    mock_db = MagicMock()
    mock_db.execute.return_value.fetchall.return_value = [
        ("TableX", "ColY", "Found a secret", 0.99)
    ]
    
    result = search_discoveries(mock_db, "secret")
    
    assert len(result) == 1
    assert result[0]["table"] == "TableX"
    assert result[0]["discovery"] == "Found a secret"
