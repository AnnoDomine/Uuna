from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.requests.request_courier import request_courier
from Tools.agents.requests.utils import request_tool_to_use
from Tools.agents.requests.utils.get_request_if_event_is_finished import is_event_finish
from Tools.toolsets import global_tool_set
from Tools.toolsets.archivist_tool_set import ARCHIVIST_TOOLS

TOOLS_MAP = {f.__name__: f for f in ARCHIVIST_TOOLS}


def request_archivist(task_id: int, event_id: int):
    """
    This function defines the hole flow how the archivist is working.

    1. Get event
    2. Loop while event is not finished (max 5 times):
      2.1 Decide tool to use
      2.2 Use tool
      2.3 Check if event is finished
    3. Create new event with output of all tools
    4. Send new event id to courier

    Args:
        task_id (int): The related task id
        event_id (int): The related event id
    """
    is_finish = False
    request_try = 0
    output = []

    try:
        event_response = global_tool_set.get_event_data(event_id=event_id)
        if "error" in event_response:
            raise Exception(event_response.get("error", "No error output"))

        input = event_response

        while not is_finish and request_try <= 5:
            request_try += 1

            tool_to_use = request_tool_to_use(input, Agents.ARCHIVIST, ARCHIVIST_TOOLS)
            output.append(tool_to_use)
            tool, props = tool_to_use["tool"], tool_to_use["props"]

            if tool is None or ARCHIVIST_TOOLS[tool] is None:
                raise Exception("No tool selected or tool not found in tool set")

            tool_func = TOOLS_MAP.get(tool)
            if not tool_func:
                raise Exception("Tool not found in tool set")

            tool_respone = tool_func(**props)
            output.append(tool_respone)
            if "error" in tool_respone:
                raise Exception(tool_respone.get("error", "No error output"))

            is_finish = is_event_finish(event_response, tool_respone, Agents.ARCHIVIST)
            input = output

        # create event with the current output
        new_event = global_tool_set.create_task_event(task_id, Agents.ARCHIVIST, Agents.COURIER, output)
        if "error" in new_event:
            raise Exception(new_event.get("error", "No error spezified while create event"))

        new_event_id = new_event.get("event_id", -1)
        if new_event_id is -1:
            raise Exception(
                f"Error while creating event for task id {task_id}. From: {Agents.ARCHIVIST} - to: {Agents.COURIER}"
            )

        request_courier(task_id, new_event_id)

    except Exception as e:
        return {"error": str(e)}
