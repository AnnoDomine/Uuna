# Tools/tests/test_db_client_unit.py
import pytest
import responses
from Tools.core.db_client import DBClient, DBResult


@pytest.fixture
def db_client():
    return DBClient(url="http://mock-db:8002")


@responses.activate
def test_execute_query(db_client):
    mock_data = {"columns": ["id", "name"], "results": [[1, "Test"]]}
    responses.add(responses.POST, "http://mock-db:8002/query", json=mock_data, status=200)

    result = db_client.execute("SELECT * FROM test")

    assert isinstance(result, DBResult)
    assert result.fetchone() == [1, "Test"]
    assert result.fetchall() == [[1, "Test"]]
    assert len(result.df()) == 1
    assert result.rowcount == 1


@responses.activate
def test_execute_non_query(db_client):
    mock_data = {"status": "success"}
    responses.add(responses.POST, "http://mock-db:8002/execute", json=mock_data, status=200)

    result = db_client.execute("INSERT INTO test VALUES (1)")

    assert result.rowcount == 1
    assert result.fetchall() == []


def test_db_result_empty():
    res = DBResult({})
    assert res.fetchone() is None
    assert res.fetchall() == []
    assert res.df().empty
    assert res.rowcount == 0
