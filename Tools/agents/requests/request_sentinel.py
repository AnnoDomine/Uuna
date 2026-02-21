from pydantic import BaseModel, Field
from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.requests.request_courier import request_courier
from Tools.toolsets import global_tool_set
from Tools.toolsets.sentinel_tool_set import SENTINEL_TOOLS
from Tools.toolsets.tools.courier.orchestration_helper import request_tool_selection, is_event_finished
from Tools.toolsets.tools.system.notify_frontend import notify_frontend

TOOLS_MAP = {f.__name__: f for f in SENTINEL_TOOLS}


class SecurityAuditStatus(BaseModel):
    is_finished: bool = Field(..., description="True if the data has been fully audited and sanitized.")
    security_verdict: str = Field(..., description="The final security assessment (e.g., 'CLEAN', 'SENSITIVE_DATA_REDACTED', 'FLAGGED').")
    reason: str = Field(..., description="Explanation of the findings and actions taken.")


def request_sentinel(task_id: str, event_id: str):
    """
    Handles data sanitization and security audits for the Sentinel.
    """
    is_finish = False
    request_try = 0
    output = []

    try:
        notify_frontend(task_id, "Sentinel: Auditing and sanitizing research data...", agent="Sentinel", type="research")
        
        event_ctx = global_tool_set.get_event_data(event_id=event_id)
        if "error" in event_ctx:
            raise Exception(event_ctx["error"])

        current_input = event_ctx

        while not is_finish and request_try < 3:
            request_try += 1

            # Decide tool to use
            tool_call = request_tool_selection(task_id, current_input, Agents.SENTINEL, SENTINEL_TOOLS)
            if "error" in tool_call:
                raise Exception(tool_call["error"])
            
            output.append(tool_call)
            tool_name, props = tool_call["tool"], tool_call["props"]

            tool_func = TOOLS_MAP.get(tool_name)
            if not tool_func:
                raise Exception(f"Tool '{tool_name}' not found in Sentinel toolset.")

            # Execute tool
            tool_result = tool_func(**props)
            output.append({"tool": tool_name, "result": tool_result})
            
            # Check if objective is reached with specialized model
            is_finish = is_event_finished(
                task_id, event_ctx, tool_result, Agents.SENTINEL, response_model=SecurityAuditStatus
            )
            current_input = output

        # Return to Courier
        new_event = global_tool_set.create_task_event(task_id, Agents.SENTINEL.value, Agents.COURIER.value, output)
        if "error" in new_event:
            raise Exception("Failed to create Sentinel result event.")

        request_courier(task_id, new_event["event_id"])

    except Exception as e:
        notify_frontend(task_id, f"Sentinel error: {e}", agent="Sentinel", type="error", level="error")
        return {"error": str(e)}
