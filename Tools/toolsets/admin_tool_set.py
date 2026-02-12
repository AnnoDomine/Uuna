# Tools/toolsets/admin_tool_set.py

# ADMIN TOOLS - ONLY FOR HUMAN USERS, NEVER FOR AGENTS
# These tools perform destructive or high-resource operations.

from .tools.analysis.compare_builds import compare_builds
from .tools.analysis.run_mass_indexing import run_mass_indexing

# Here we will add more administrative tools like registry refreshing,
# build synchronization, and data cleaning.

ADMIN_TOOLS = [
    compare_builds,
    run_mass_indexing,
]
