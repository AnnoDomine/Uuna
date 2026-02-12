# Tools/toolsets/global_tool_set.py

from .tools.database.update_global_knowledge import update_global_knowledge

# Global tools are available to ALL agents.
GLOBAL_TOOLS = [
    update_global_knowledge,
]
