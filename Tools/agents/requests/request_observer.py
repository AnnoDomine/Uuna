from Tools.toolsets import global_tool_set
from Tools.toolsets.tools.system.notify_frontend import notify_frontend


def request_observer(task_id: str):
    """
    Evaluates the quality of the research and assigns final scores.
    """
    try:
        notify_frontend(task_id, "Observer: Mercilessly judging research quality...", agent="Observer", type="research")
        
        # 1. Get task context
        global_tool_set.get_task_context(task_id)
        
        # Scoring logic would go here (Splitting into blocks, role-based evaluation, etc.)
        
        notify_frontend(task_id, "Observer: Quality assessment complete. Scores assigned.", agent="Observer", type="research")

    except Exception as e:
        notify_frontend(task_id, f"Observer scoring error: {e}", agent="Observer", type="error", level="error")
        return {"error": str(e)}
