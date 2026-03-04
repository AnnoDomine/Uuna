from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.requests.request_courier import request_courier
from Tools.core.config_manager import get_config
from Tools.toolsets import global_tool_set
from Tools.toolsets.cartographer_tool_set import CARTOGRAPHER_TOOLS
from Tools.toolsets.tools.courier.orchestration_helper import is_event_finished, request_tool_selection
from Tools.toolsets.tools.system.notify_frontend import notify_frontend

TOOLS_MAP = {f.__name__: f for f in CARTOGRAPHER_TOOLS}


def request_cartographer(task_id: str, event_id: str):
    """
    Handles data visualization and mermaid diagram generation for the Cartographer.
    """
    is_finish = False
    request_try = 0
    output = []

    max_tries = get_config().tasks.max_tries_cartorapher

    try:
        notify_frontend(task_id, "Cartographer: Visualizing data structures...", agent="Cartographer", type="research")

        event_ctx = global_tool_set.get_event_data(event_id=event_id)
        if "error" in event_ctx:
            raise Exception(event_ctx["error"])

        output.append(event_ctx)

        while not is_finish and request_try < max_tries:  # Cartographer usually needs fewer steps
            request_try += 1

            # Decide tool to use
            tool_call = request_tool_selection(task_id, output, Agents.CARTOGRAPHER, CARTOGRAPHER_TOOLS)
            if "error" in tool_call:
                raise Exception(tool_call["error"])

            output.append(tool_call)
            tool_name = tool_call.get("tool")
            props = tool_call.get("props", {})

            if tool_name and tool_name.lower() != "none":
                tool_func = TOOLS_MAP.get(tool_name)
                if not tool_func:
                    output.append({"error": f"Tool '{tool_name}' not found in Cartographer toolset."})
                    continue

                # Execute tool
                tool_result = tool_func(**props)
                output.append({"tool": tool_name, "result": tool_result})

            # Check if objective is reached
            is_finish = is_event_finished(task_id, event_ctx, output, Agents.CARTOGRAPHER)

        # Return to Courier
        new_event = global_tool_set.create_task_event(task_id, Agents.CARTOGRAPHER.value, Agents.COURIER.value, output)
        if "error" in new_event:
            raise Exception("Failed to create Cartographer result event.")

        request_courier(task_id, new_event["event_id"])

    except Exception as e:
        notify_frontend(task_id, f"Cartographer error: {e}", agent="Cartographer", type="error", level="error")
        return {"error": str(e)}
