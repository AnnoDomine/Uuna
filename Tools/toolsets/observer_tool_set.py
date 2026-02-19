# Tools/toolsets/observer_tool_set.py

from .tools.audit.evaluate_agent_output import evaluate_agent_output
from .tools.audit.check_logical_consistency import check_logical_consistency
from .tools.audit.grant_final_verdict import grant_final_verdict

# The Observer mercilessly judges accuracy, formatting, and logic.
OBSERVER_TOOLS = [
    evaluate_agent_output,
    check_logical_consistency,
    grant_final_verdict,
]
