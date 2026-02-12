# Tools/toolsets/librarian_tool_set.py

from .tools.system.create_research_task import create_research_task
from .tools.system.get_verified_results import get_verified_results

# The Librarian is the interface between the human and the archive.
LIBRARIAN_TOOLS = [
    create_research_task,
    get_verified_results,
]
