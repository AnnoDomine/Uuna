import requests
import time
import subprocess
import sys

URL = "http://127.0.0.1:8001"

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
        print(f"❌ /query failed: {e}")
        return False

    # 2. Execute (Temporary Table)
    try:
        print("Testing /execute (CREATE TEMP TABLE)...")
        r = requests.post(f"{URL}/execute", json={"sql": "CREATE TABLE IF NOT EXISTS research.test_val (val INTEGER)", "params": []}, timeout=5)
        r.raise_for_status()
        print("✅ /execute (CREATE) successful")

        print("Testing /execute (INSERT)...")
        r = requests.post(f"{URL}/execute", json={"sql": "INSERT INTO research.test_val VALUES (?)", "params": [42]}, timeout=5)
        r.raise_for_status()
        print("✅ /execute (INSERT) successful")

        print("Verifying INSERT via /query...")
        r = requests.post(f"{URL}/query", json={"sql": "SELECT val FROM research.test_val WHERE val = 42", "params": []}, timeout=5)
        r.raise_for_status()
        res = r.json()
        print(f"Verification Response: {res}")
        assert res["results"][0][0] == 42
        print("✅ Data persistence verified")
        
        # Cleanup
        requests.post(f"{URL}/execute", json={"sql": "DROP TABLE research.test_val", "params": []})
        print("✅ Cleanup successful")
        
    except Exception as e:
        print(f"❌ /execute test sequence failed: {e}")
        return False

    print("\n>>> ALL DB SERVICE TESTS PASSED <<<")
    return True

if __name__ == "__main__":
    # Start service in background if not running
    service_proc = subprocess.Popen([".venv/bin/python3", "Tools/db_service.py"])
    time.sleep(3) # Wait for startup
    
    success = test_service()
    
    # Shutdown service
    service_proc.terminate()
    sys.exit(0 if success else 1)
