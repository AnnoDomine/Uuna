from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.requests.agent_models import LoreResearchStatus
from Tools.core.config_manager import get_config
from Tools.toolsets import global_tool_set
from Tools.toolsets.expedition_group_tool_set import EXPEDITION_GROUP_TOOLS
from Tools.toolsets.tools.courier.orchestration_helper import is_event_finished, request_tool_selection
from Tools.toolsets.tools.system.notify_frontend import notify_frontend

TOOLS_MAP = {f.__name__: f for f in EXPEDITION_GROUP_TOOLS}


def request_expedition_group(task_id: str, event_id: str):
    """
    Handles online research and lore exploration for the Expedition Group.
    """
    from Tools.agents.requests.request_sentinel import request_sentinel

    is_finish = False
    request_try = 0
    output = []

    max_tries = get_config().tasks.max_tries_expedition_group

    try:
        notify_frontend(
            task_id, "Expedition Group: Starting online research...", agent="Expedition Group", type="research"
        )

        task_ctx = global_tool_set.get_task_context(task_id=task_id)
        if "error" in task_ctx:
            raise Exception(task_ctx["error"])

        event_ctx = global_tool_set.get_event_data(event_id=event_id)
        if "error" in event_ctx:
            raise Exception(event_ctx["error"])

        output.append(event_ctx)

        while not is_finish and request_try < max_tries:
            request_try += 1

            # Decide tool to use with task context
            tool_call = request_tool_selection(
                task_id, output, Agents.EXPEDITION_GROUP, EXPEDITION_GROUP_TOOLS, task_context=task_ctx
            )
            if "error" in tool_call:
                raise Exception(tool_call["error"])

            output.append(tool_call)
            tool_name = tool_call.get("tool")
            props = tool_call.get("props", {})

            if tool_name and tool_name.lower() != "none":
                tool_func = TOOLS_MAP.get(tool_name)
                if not tool_func:
                    output.append({"error": f"Tool '{tool_name}' not found in Expedition Group toolset."})
                    continue

                # Execute tool
                tool_result = tool_func(**props)
                output.append({"tool": tool_name, "result": tool_result})

            # Check if objective is reached with specialized model and full history
            is_finish = is_event_finished(
                task_id, event_ctx, output, Agents.EXPEDITION_GROUP, response_model=LoreResearchStatus
            )

        # Transition to Sentinel for data cleaning/security check
        new_event = global_tool_set.create_task_event(
            task_id, Agents.EXPEDITION_GROUP.value, Agents.SENTINEL.value, output
        )
        if "error" in new_event:
            raise Exception("Failed to create research result event.")

        request_sentinel(task_id, new_event["event_id"])

    except Exception as e:
        notify_frontend(task_id, f"Expedition Group error: {e}", agent="Expedition Group", type="error", level="error")
        return {"error": str(e)}
