from Tools.agents.requests.request_observer import request_observer
from Tools.toolsets import global_tool_set
from Tools.toolsets.tools.system.notify_frontend import notify_frontend


def request_tinker(task_id: str):
    """
    Calculates the 'Max Potential' score for a task and its events.
    """
    try:
        notify_frontend(task_id, "Tinker: Calculating quantitative difficulty scores...", agent="Tinker", type="research")
        
        # 1. Get task context
        global_tool_set.get_task_context(task_id)
        
        # Logic for calculating scores would go here...
        # For now, we just pass through to the Observer
        
        request_observer(task_id)

    except Exception as e:
        notify_frontend(task_id, f"Tinker scoring error: {e}", agent="Tinker", type="error", level="error")
        return {"error": str(e)}
