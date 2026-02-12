# Tools/toolsets/global_tool_set.py

from .tools.database.update_global_knowledge import update_global_knowledge
from .tools.registry.check_build_status import check_build_status
from .tools.system.get_my_skills import get_my_skills
from .tools.system.get_task_context import get_task_context
from .tools.events.log_event_reasoning import log_event_reasoning
from .tools.events.get_event_data import get_event_data
from .tools.research.query_vector_memory import query_vector_memory
from .tools.research.search_discoveries import search_discoveries

# Global tools are available to ALL agents.
GLOBAL_TOOLS = [
    update_global_knowledge,
    check_build_status,
    get_my_skills,
    get_task_context,
    log_event_reasoning,
    get_event_data,
    query_vector_memory,
    search_discoveries,
]
