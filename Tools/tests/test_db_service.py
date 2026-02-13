import requests
import time
import subprocess
import sys
import pytest
import os

URL = "http://127.0.0.1:8002"
TEST_DB_PATH = "Data/WoW_Test.duckdb"


@pytest.fixture(scope="module", autouse=True)
def db_service():
    # Ensure test DB is clean
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    # Start service
    print("\nStarting DB Service for tests (MOCKED DB)...")
    script_path = os.path.join(os.getcwd(), "Tools/core/db_service.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    env["WOW_DB_PATH"] = TEST_DB_PATH

    # Use uv run if available, otherwise python3
    cmd = ["uv", "run", "python", "-u", script_path]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, start_new_session=True)
    except FileNotFoundError:
        proc = subprocess.Popen(
            ["python3", "-u", script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            start_new_session=True,
        )

    # Wait for service to be READY (not just running)
    ready = False
    for _ in range(15):
        time.sleep(1)
        try:
            r = requests.post(f"{URL}/query", json={"sql": "SELECT 1", "params": []}, timeout=1)
            if r.status_code == 200:
                ready = True
                break
        except requests.exceptions.ConnectionError:
            continue

    if not ready:
        proc.terminate()
        pytest.fail("DB Service failed to start or initialize database within timeout")

    yield
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()

    # Cleanup test DB
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception as e:
            print(f"Warning: Could not remove test DB: {e}")


def test_service():
    print(">>> Starting DB Service Test <<<")

    # 1. Simple Query
    try:
        print("Testing /query (SELECT 1)...")
        r = requests.post(f"{URL}/query", json={"sql": "SELECT 1", "params": []}, timeout=5)
        r.raise_for_status()
        res = r.json()
        print(f"Response: {res}")
        assert res["results"][0][0] == 1
        print("✅ /query successful")
    except Exception as e:
        pytest.fail(f"/query failed: {e}")

    # 2. Execute (Temporary Table)
    try:
        print("Testing /execute (CREATE TEMP TABLE)...")
        r = requests.post(
            f"{URL}/execute",
            json={"sql": "CREATE TABLE IF NOT EXISTS research.test_val (val INTEGER)", "params": []},
            timeout=5,
        )
        r.raise_for_status()
        print("✅ /execute (CREATE) successful")

        print("Testing /execute (INSERT)...")
        r = requests.post(
            f"{URL}/execute", json={"sql": "INSERT INTO research.test_val VALUES (?)", "params": [42]}, timeout=5
        )
        r.raise_for_status()
        print("✅ /execute (INSERT) successful")

        print("Verifying INSERT via /query...")
        r = requests.post(
            f"{URL}/query", json={"sql": "SELECT val FROM research.test_val WHERE val = 42", "params": []}, timeout=5
        )
        r.raise_for_status()
        res = r.json()
        print(f"Verification Response: {res}")
        assert res["results"][0][0] == 42
        print("✅ Data persistence verified")

        # Cleanup
        requests.post(f"{URL}/execute", json={"sql": "DROP TABLE research.test_val", "params": []})
        print("✅ Cleanup successful")

    except Exception as e:
        pytest.fail(f"/execute test sequence failed: {e}")

    print("\n>>> ALL DB SERVICE TESTS PASSED <<<")


if __name__ == "__main__":
    # If run directly, just run the test
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    script_path = os.path.join(os.getcwd(), "Tools/core/db_service.py")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    env["WOW_DB_PATH"] = TEST_DB_PATH

    # Start service in background
    service_proc = subprocess.Popen(["uv", "run", "python", "-u", script_path], env=env, start_new_session=True)

    # Wait for service to be READY
    ready = False
    for _ in range(15):
        time.sleep(1)
        try:
            r = requests.post(f"{URL}/query", json={"sql": "SELECT 1", "params": []}, timeout=1)
            if r.status_code == 200:
                ready = True
                break
        except requests.exceptions.ConnectionError:
            continue

    if not ready:
        print("❌ DB Service failed to start")
        service_proc.terminate()
        sys.exit(1)

    try:
        test_service()
        success = True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        success = False

    # Shutdown service
    service_proc.terminate()
    try:
        service_proc.wait(timeout=5)
    except Exception:
        service_proc.kill()

    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    sys.exit(0 if success else 1)
