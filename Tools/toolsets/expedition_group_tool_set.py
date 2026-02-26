# Tools/toolsets/expedition_group_tool_set.py

from .tools.research.fetch_web_content import fetch_web_content
from .tools.research.get_wago_structure import get_wago_structure
from .tools.research.search_wow_wiki import search_wow_wiki
from .tools.research.query_vector_memory import query_vector_memory
from .tools.research.search_discoveries import search_discoveries

# Expedition Group tools are focused on online research and lore context.
EXPEDITION_GROUP_TOOLS = [
    fetch_web_content,
    get_wago_structure,
    search_wow_wiki,
    query_vector_memory,
    search_discoveries,
]
