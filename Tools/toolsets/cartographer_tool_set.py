# Tools/toolsets/cartographer_tool_set.py

# Import tool functions from their respective modules
from .tools.filesystem.save_mermaid_diagram import save_mermaid_diagram
from .tools.database.get_confirmed_mappings import get_confirmed_mappings
from .tools.analysis.generate_relationship_map import generate_relationship_map

# This toolset contains all tools derived from the Cartographer agent's functions.
CARTOGRAPHER_TOOLS = [
    save_mermaid_diagram,
    get_confirmed_mappings,
    generate_relationship_map,
]
