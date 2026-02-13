import requests
import time
from loguru import logger


def penalize_agent():
    url = "http://127.0.0.1:8001/score/assign"
    data = {"task_id": "d9d5a3cb-a88f-48b0-9c98-991c2f7d384b", "percent": 15.0}

    logger.info("Observer is waiting for API to apply penalty...")
    for _ in range(10):
        try:
            r = requests.post(url, json=data, timeout=5)
            if r.status_code == 200:
                logger.success("Penalty successfully applied to ScoreBoard!")
                return
            else:
                logger.warning(f"API returned {r.status_code}: {r.text}")
        except:
            pass
        time.sleep(2)
    logger.error("Failed to apply penalty after multiple retries.")


if __name__ == "__main__":
    penalize_agent()
