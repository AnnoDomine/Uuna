# Tools/toolsets/observer_tool_set.py

from .tools.audit.evaluate_agent_output import evaluate_agent_output

OBSERVER_TOOLS = [
    evaluate_agent_output,
]
