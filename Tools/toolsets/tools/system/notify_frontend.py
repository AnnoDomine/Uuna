import os
from typing import Any, Dict, Literal

import httpx

from .get_task_context import get_task_context


def notify_frontend(
    task_id: str,
    message: str,
    agent: str = "System",
    type: Literal["research", "response", "error"] = "research",
    level: str = "info",
) -> Dict[str, Any]:
    """
    Sends a status update or notification to the TUI frontend.

    Args:
    - task_id: The UUID of the research task.
    - message: The notification message to display.
    - agent: The role name of the agent sending the notification.
    - type: The type of notification (research, response, error).
    - level: The severity level (info, warning, error).
    """
    port = os.getenv("TUI_SIGNAL_PORT", "3800")
    url = f"http://localhost:{port}/update"

    try:
        # Get full task context to provide meaningful updates to the frontend
        # This is optional but helpful for the 'response' type
        task_ctx = None
        if type == "response":
            task_ctx = get_task_context(task_id)

        payload = {
            "task_id": task_id,
            "agent": agent,
            "type": type,
            "message": message,
            "level": level,
            "task_context": task_ctx,
        }

        with httpx.Client(timeout=5.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            return {"status": "success"}

    except Exception as e:
        print(f"WARNING: Frontend notification failed: {e}")
        return {"status": "error", "message": str(e)}
