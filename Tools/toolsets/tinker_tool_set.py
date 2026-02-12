# Tools/toolsets/tinker_tool_set.py

from .tools.tinker.assess_complexity import assess_complexity
from .tools.tinker.assign_potential_score import assign_potential_score

# The Tinker defines the "Reward Space" by analyzing task complexity.
TINKER_TOOLS = [
    assess_complexity,
    assign_potential_score,
]
