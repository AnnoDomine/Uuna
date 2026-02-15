from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.requests.utils.get_valid_return_json import request_with_schema


def is_event_finish(input, output, role: Agents):
    """
    The function request the AI agent, if the agent is finished with the event.
    """
    payload = {
        "messages": [
            {
                "role": "system",
                "content": "Compare the input from the current event with the output and decide, if the event is finished.",
            },
            {"role": "user", "content": f"INPUT:\n{input}\n\nOUTPUT:\n{output}"},
        ]
    }

    response_obj = {"is_finished": False}

    res = request_with_schema(response_obj, payload, role)

    is_finished = res.get("is_finished", False) in [True, "true", "1", 1]

    return is_finished
