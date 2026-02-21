from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.requests.request_sentinel import request_sentinel
from Tools.agents.requests.agent_models import LoreResearchStatus
from Tools.toolsets import global_tool_set
from Tools.toolsets.expedition_group_tool_set import EXPEDITION_GROUP_TOOLS
from Tools.toolsets.tools.courier.orchestration_helper import request_tool_selection, is_event_finished
from Tools.toolsets.tools.system.notify_frontend import notify_frontend

TOOLS_MAP = {f.__name__: f for f in EXPEDITION_GROUP_TOOLS}


def request_expedition_group(task_id: str, event_id: str):
    """
    Handles online research and lore exploration for the Expedition Group.
    """
    is_finish = False
    request_try = 0
    output = []

    try:
        notify_frontend(task_id, "Expedition Group: Starting online research...", agent="Expedition Group", type="research")
        
        event_ctx = global_tool_set.get_event_data(event_id=event_id)
        if "error" in event_ctx:
            raise Exception(event_ctx["error"])

        current_input = event_ctx

        while not is_finish and request_try < 5:
            request_try += 1

            # Decide tool to use
            tool_call = request_tool_selection(task_id, current_input, Agents.EXPEDITION_GROUP, EXPEDITION_GROUP_TOOLS)
            if "error" in tool_call:
                raise Exception(tool_call["error"])
            
            output.append(tool_call)
            tool_name, props = tool_call["tool"], tool_call["props"]

            tool_func = TOOLS_MAP.get(tool_name)
            if not tool_func:
                raise Exception(f"Tool '{tool_name}' not found in Expedition Group toolset.")

            # Execute tool
            tool_result = tool_func(**props)
            output.append({"tool": tool_name, "result": tool_result})
            
            # Check if objective is reached with specialized model
            is_finish = is_event_finished(
                task_id, event_ctx, tool_result, Agents.EXPEDITION_GROUP, response_model=LoreResearchStatus
            )
            current_input = output

        # Transition to Sentinel for data cleaning/security check
        new_event = global_tool_set.create_task_event(task_id, Agents.EXPEDITION_GROUP.value, Agents.SENTINEL.value, output)
        if "error" in new_event:
            raise Exception("Failed to create research result event.")

        request_sentinel(task_id, new_event["event_id"])

    except Exception as e:
        notify_frontend(task_id, f"Expedition Group error: {e}", agent="Expedition Group", type="error", level="error")
        return {"error": str(e)}
