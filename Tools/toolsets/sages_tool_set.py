# Tools/toolsets/sages_tool_set.py

from .tools.audit.check_logical_consistency import check_logical_consistency
from .tools.audit.grant_final_verdict import grant_final_verdict

# The Sages act as the supreme authority on knowledge quality.
# They are the final gatekeepers before information is presented to the user.
SAGES_TOOLS = [
    check_logical_consistency,
    grant_final_verdict,
]
