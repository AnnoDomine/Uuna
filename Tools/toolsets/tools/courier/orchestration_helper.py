import inspect
from typing import Any, Callable, Dict, List

from Tools.agents.get_agent_skill_set import Agents
from Tools.core.ai_schema_validator import request_with_schema
from Tools.toolsets.tools.system.notify_frontend import notify_frontend


def _parse_tool_props_schema(schema: dict) -> dict:
    """Helper to refine the tool selection schema."""
    schema["properties"]["tool"]["description"] = "The selected tool to use"
    schema["properties"]["props"]["additionalProperties"] = True
    schema["properties"]["props"]["description"] = "Input parameters for the selected tool"
    return schema


def get_tool_definitions(functions: List[Callable]) -> List[Dict[str, Any]]:
    """
    Parses tool functions into a standardized list of definitions for AI prompting.
    """
    definitions = []

    for func in functions:
        doc = inspect.getdoc(func) or ""
        lines = doc.split("\n")
        tool_description = lines[0] if lines else "No description available."

        signature = inspect.signature(func)
        props = {}

        for name, param in signature.parameters.items():
            prop_desc = "No description"
            for line in lines:
                if f"- {name}:" in line:
                    prop_desc = line.split(":")[-1].strip()

            if param.annotation is int:
                val = 0
            elif param.annotation is bool:
                val = False
            else:
                val = "string"

            props[name] = {
                "value_example": val,
                "description": prop_desc,
                "type": str(param.annotation.__name__) if hasattr(param.annotation, "__name__") else "any",
            }

        definitions.append({"tool": func.__name__, "description": tool_description, "props": props})

    return definitions


def parse_tools_to_prompt(tools: List[Callable]) -> str:
    """Formats a list of tool functions into a readable string for agent prompts."""
    tool_defs = get_tool_definitions(tools)
    tool_list = []

    for td in tool_defs:
        props_details = "\n- ".join(
            [f"{p_name} ({p_info['type']}): {p_info['description']}" for p_name, p_info in td["props"].items()]
        )
        tool_info = f"TOOL: {td['tool']}\nDESCRIPTION: {td['description']}\nARGUMENTS:\n- {props_details}"
        tool_list.append(tool_info)

    separator = "\n" + "-" * 30 + "\n"
    return separator + separator.join(tool_list) + separator


def request_tool_selection(task_id: str, event: dict, role: Agents, tools: List[Callable]) -> dict:
    """
    Asks the agent to select the best tool for the current task context.
    """
    notify_frontend(task_id, f"{role.value}: Selecting optimal tool...", agent=role.value, type="research")

    try:
        event_input = event.get("input_data", "No input data")
        tools_prompt = parse_tools_to_prompt(tools)

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Based on the EVENT INPUT, select the best tool and provide the necessary parameters.",
                },
                {
                    "role": "user",
                    "content": f"EVENT INPUT:\n{event_input}\n\nAVAILABLE TOOLS:\n{tools_prompt}",
                },
            ],
        }

        response_template = {"tool": "string", "props": {}}
        result = request_with_schema(response_template, payload, role, _parse_tool_props_schema)

        if "tool" in result:
            notify_frontend(task_id, f"{role.value}: Executing tool '{result['tool']}'", agent=role.value, type="research")

        return result

    except Exception as e:
        notify_frontend(task_id, f"Error during tool selection: {e}", agent=role.value, type="error", level="error")
        return {"error": str(e)}


def is_event_finished(task_id: str, input_data: any, output_data: any, role: Agents) -> bool:
    """
    Asks the agent if the current event is fully resolved.
    """
    try:
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Compare the input from the current event with the output and decide if the event is finished.",
                },
                {"role": "user", "content": f"INPUT:\n{input_data}\n\nOUTPUT:\n{output_data}"},
            ]
        }

        response_template = {"is_finished": False}
        res = request_with_schema(response_template, payload, role)

        finished = res.get("is_finished", False) in [True, "true", "1", 1]
        
        if finished:
            notify_frontend(task_id, f"{role.value}: Event completed.", agent=role.value, type="research")
            
        return finished

    except Exception:
        return False
