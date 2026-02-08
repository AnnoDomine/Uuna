import datetime
import requests
import subprocess
import asyncio
import atexit
import os

API_URL = "http://127.0.0.1:8001"


async def ensure_backend(self) -> None:
    """Ensures the backend is running, starting it if necessary."""
    try:
        r = requests.get(f"{API_URL}/health", timeout=1)
        if r.status_code == 200:
            self.log_view.write_line(
                f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Backend online."
            )
            self.update_status()
            return
    except:
        pass

    self.log_view.write_line(
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] WARNING: Backend not ready, starting..."
    )

    env = os.environ.copy()

    self.backend_process = subprocess.Popen(
        [
            ".venv/bin/python3",
            "-u",
            "-m",
            "uvicorn",
            "Tools.core.api.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8001",
        ],
        stdout=open("Data/logs/api_out.log", "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
        env=env,
    )
    # Safety net: Ensure process is killed on exit
    atexit.register(self.terminate_backend)

    for i in range(1, 11):
        self.log_view.write_line(
            f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Backend Try {i}/10..."
        )
        await asyncio.sleep(2)
        try:
            r = requests.get(f"{API_URL}/health", timeout=1)
            if r.status_code == 200:
                self.log_view.write_line(
                    f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Backend started."
                )
                self.update_status()
                return
        except:
            pass

    self.log_view.write_line(
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ERROR: Backend start failed."
    )
