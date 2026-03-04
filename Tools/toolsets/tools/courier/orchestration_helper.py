import inspect
import json
from typing import Any, Callable, Dict, List, Type, Union

from pydantic import BaseModel, Field

from Tools.agents.get_agent_skill_set import Agents
from Tools.core.ai_schema_validator import request_with_schema
from Tools.core.shared_debugger import debugger
from Tools.toolsets.tools.system.notify_frontend import notify_frontend


class DefaultToolSelection(BaseModel):
    tool: str = Field(..., description="The name of the tool to execute.")
    props: Dict[str, Any] = Field(default_factory=dict, description="The dictionary of arguments for the tool.")


class DefaultEventStatus(BaseModel):
    is_finished: bool = Field(..., description="True if the objective of the current event is fully achieved.")
    reason: str = Field(..., description="The rationale behind the decision.")


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


def request_tool_selection(
    task_id: str,
    event: Union[dict, list],
    role: Agents,
    tools: List[Callable],
    response_model: Type[BaseModel] = DefaultToolSelection,
    task_context: dict = None,
) -> dict:
    """
    Asks the agent to select the best tool for the current task context.
    """
    agent_name = role.value if hasattr(role, "value") else str(role)
    debugger.add_log(
        f"Agent {agent_name} selecting tool for Task {task_id}", agent=agent_name, process="Orchestration:ToolSelection"
    )
    notify_frontend(task_id, f"{agent_name}: Selecting optimal tool...", agent=agent_name, type="research")

    try:
        # Handle both initial event (dict) and loop history (list)
        if isinstance(event, dict):
            event_input = event.get("input_data", "No input data")
        else:
            # For lists, provide a summarized string representation of the history
            event_input = json.dumps(event, indent=2)

        task_info = ""
        if task_context:
            task_info = f"\n\n======= ONLY CONTEXT, NOT FOR TOOL SELECTION START ======\nTASK CONTEXT:\n- Objective: {task_context.get('task', {}).get('original_query')}\n- BUILDS: {task_context.get('task', {}).get('assigned_builds')}\n======= ONLY CONTEXT, NOT FOR TOOL SELECTION END ======\n\n"

        tools_prompt = parse_tools_to_prompt(tools)

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": f"You are the {agent_name}. Based on the EVENT INPUT and the TASK CONTEXT, select the best tool and provide the necessary parameters.{task_info}",
                },
                {
                    "role": "user",
                    "content": f"EVENT INPUT:\n{event_input}\n\nAVAILABLE TOOLS:\n{tools_prompt}",
                },
            ],
        }

        notify_frontend(task_id, f"{agent_name} Tools: {tools_prompt}", agent=agent_name, type="research")

        result = request_with_schema(response_model, payload, role)

        if "tool" in result:
            debugger.add_log(
                f"Selected tool: {result['tool']}",
                agent=agent_name,
                level="SUCCESS",
                process="Orchestration:ToolSelection",
            )
            notify_frontend(
                task_id, f"{agent_name}: Executing tool '{result['tool']}'", agent=agent_name, type="research"
            )

        return result

    except Exception as e:
        debugger.add_log(
            f"Tool selection failed: {e}", agent=agent_name, level="ERROR", process="Orchestration:ToolSelection"
        )
        notify_frontend(task_id, f"Error during tool selection: {e}", agent=agent_name, type="error", level="error")
        return {"error": str(e)}


def is_event_finished(
    task_id: str, input_data: any, output_data: any, role: Agents, response_model: Type[BaseModel] = DefaultEventStatus
) -> bool:
    """
    Asks the agent if the current event is fully resolved.
    """
    agent_name = role.value if hasattr(role, "value") else str(role)
    try:
        # Format complex data for the prompt
        formatted_input = json.dumps(input_data, indent=2) if not isinstance(input_data, str) else input_data
        formatted_output = json.dumps(output_data, indent=2) if not isinstance(output_data, str) else output_data

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "Compare the input from the current event with the output and decide if the event is finished.",
                },
                {"role": "user", "content": f"INPUT:\n{formatted_input}\n\nOUTPUT:\n{formatted_output}"},
            ]
        }

        res = request_with_schema(response_model, payload, role)

        finished = res.get("is_finished", False) in [True, "true", "1", 1]

        if finished:
            debugger.add_log(
                f"Event finished for {agent_name}. Reason: {res.get('reason', 'N/A')}",
                agent=agent_name,
                level="SUCCESS",
                process="Orchestration:CompletionCheck",
            )
            notify_frontend(
                task_id,
                f"{agent_name}: Event completed. Reason: {res.get('reason', 'N/A')}",
                agent=agent_name,
                type="research",
            )
        else:
            debugger.add_log(
                f"Event continues for {agent_name}. Reason: {res.get('reason', 'N/A')}",
                agent=agent_name,
                process="Orchestration:CompletionCheck",
            )

        return finished

    except Exception as e:
        debugger.add_log(
            f"Completion check crashed: {e}", agent=agent_name, level="ERROR", process="Orchestration:CompletionCheck"
        )
        return False
