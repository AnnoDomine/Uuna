# Tools/toolsets/courier_tool_set.py

from .tools.courier.get_role_capabilities import get_role_capabilities
from .tools.courier.create_task_event import create_task_event
from .tools.courier.update_task_status import update_task_status

# The Courier is the only agent with these administrative orchestration tools.
COURIER_TOOLS = [
    get_role_capabilities,
    create_task_event,
    update_task_status,
]
