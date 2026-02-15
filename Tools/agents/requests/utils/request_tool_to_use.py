import inspect
from typing import Any, Callable, Dict, List

from Tools.agents.get_agent_skill_set import Agents
from Tools.agents.requests.utils.get_valid_return_json import request_with_schema


def parse_tool_props_schema(schema: dict) -> dict:
    schema["properties"]["tool"]["description"] = "The selected tool to use"
    schema["properties"]["props"]["additionalProperties"] = True
    schema["properties"]["props"]["description"] = "Input parameters for the selected tool"
    return schema


def get_tool_definitions(functions: List[Callable]) -> List[Dict[str, Any]]:
    """
    Parse the tools and there related arguments to map a desciption for the tool and the arguments.
    This parser do only works with a correct strict pattern:
    ```
    <tool_description>

    Args:
    - <arg_name>: <arg_description>
    # ... more args
    ```
    """
    definitions = []

    for func in functions:
        # Extract the tool description
        doc = inspect.getdoc(func) or ""
        lines = doc.split("\n")
        tool_description = lines[0] if lines else "No description available."

        # Extrahiere die Parameter (Props)
        signature = inspect.signature(func)
        props = {}

        for name, param in signature.parameters.items():
            # Search for the doc string.
            prop_desc = "No description"
            for line in lines:
                if f"- {name}:" in line or f":param {name}:" in line:
                    prop_desc = line.split(":")[-1].strip()

            # Define the type for genson
            if param.annotation is int:
                val = 0
            elif param.annotation is bool:
                val = False
            else:
                val = "string"

            # Store the value
            props[name] = {
                "value_example": val,
                "description": prop_desc,
                "type": str(param.annotation.__name__) if hasattr(param.annotation, "__name__") else "any",
            }

        definitions.append({"tool": func.__name__, "description": tool_description, "props": props})

    return definitions


def parse_tools_list_to_promp(tools: List[Callable]) -> str:
    # Get the tool definition
    tool_defs = get_tool_definitions(tools)

    tool_list = []
    # Fill the tool list
    for td in tool_defs:
        props_details = "\n- ".join(
            [f"- {p_name} ({p_info['type']}): {p_info['description']}" for p_name, p_info in td["props"].items()]
        )

        tool_info = f"TOOL: {td['tool']}\nDESCRIPTION: {td['description']}\nARGUMENTS:\n{props_details}"

        tool_list.append(tool_info)

    # Return the parsed string with the list of all tools, description and the related arguments with description of the arguments
    return (
        "\n----------------------\n----------------------\n"
        + "\n----------------------\n".join(tool_list)
        + "\n----------------------\n----------------------\n"
    )


def request_tools_to_use(event, role: Agents, tools: List[Callable]):
    """
    Request to KI which tools have to be used.
    Args:
    - event: The related event as context
    - role: The agent which select the tool to use
    - tools: The toolset
    Return:
    - Response with the tool to use
    """
    try:
        event_input = event.get("input_data", "No input data")

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": ("Based on the EVENT INPUT, select the best tool and provide the necessary parameters."),
                },
                {
                    "role": "user",
                    "content": f"EVENT INPUT:\n{event_input}\n\nAVAILABLE TOOLS:\n{parse_tools_list_to_promp(tools)}",
                },
            ],
        }

        response_dict = {"tool": "string", "props": {}}

        return request_with_schema(response_dict, payload, role, parse_tool_props_schema)
    except Exception as e:
        return {"error": str(e)}
