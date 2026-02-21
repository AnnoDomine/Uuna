from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.requests.request_observer import request_observer
from Tools.agents.requests.agent_models import TinkerAssessment
from Tools.toolsets import global_tool_set
from Tools.toolsets.tinker_tool_set import assign_potential_score
from Tools.core.ai_schema_validator import request_with_schema
from Tools.toolsets.tools.system.notify_frontend import notify_frontend


def request_tinker(task_id: str):
    """
    Calculates the 'Max Potential' score for a task and its events.
    """
    try:
        notify_frontend(task_id, "Tinker: Calculating quantitative difficulty scores...", agent="Tinker", type="research")
        
        # 1. Get task context and history
        task_ctx = global_tool_set.get_task_context(task_id=task_id)
        if "error" in task_ctx:
            raise Exception(task_ctx["error"])
            
        history = task_ctx.get("history", [])
        if not history:
            notify_frontend(task_id, "Tinker: No history found to score.", agent="Tinker", type="research", level="warning")
            request_observer(task_id)
            return

        # 2. AI assessment of complexity
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are the Tinker. Analyze the task history and assign a 'Potential Score' (0-1000) to each event based on its technical complexity and volume of data processed.",
                },
                {"role": "user", "content": f"TASK: {task_ctx['task']}\n\nHISTORY:\n{history}"},
            ]
        }

        assessment = request_with_schema(TinkerAssessment, payload, Agents.TINKER)
        
        if "error" in assessment:
            raise Exception(assessment["error"])

        # 3. Apply scores to database
        for item in assessment["assessments"]:
            assign_potential_score(event_id=item["event_id"], potential=item["potential_score"])
            
        notify_frontend(task_id, f"Tinker: Quantitative scoring complete for {len(assessment['assessments'])} events.", agent="Tinker", type="research")
        
        # 4. Hand over to Observer
        request_observer(task_id)

    except Exception as e:
        notify_frontend(task_id, f"Tinker scoring error: {e}", agent="Tinker", type="error", level="error")
        return {"error": str(e)}
