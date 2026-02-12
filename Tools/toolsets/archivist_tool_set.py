# Tools/toolsets/archivist_tool_set.py

# Import tool functions from their respective modules
from .tools.database.find_value import find_value
from .tools.database.check_ids import check_ids
from .tools.database.find_column_references import find_column_references
from .tools.analysis.extract_features import extract_features_for_build
from .tools.analysis.guess_table_reference import guess_table_reference
from .tools.analysis.map_column_references_workflow import map_column_references_workflow
from .tools.database.save_discovery import save_discovery
from .tools.database.save_attempt import save_attempt
from .tools.database.get_last_attempt import get_last_attempt
from .tools.analysis.perform_column_discovery import perform_column_discovery
from .tools.analysis.perform_column_mapping import perform_column_mapping

# The toolset is a list of the imported tool functions/classes.
# This list will be used by the agent orchestration system to grant capabilities.
ARCHIVIST_TOOLS = [
    find_value,
    check_ids,
    find_column_references,
    extract_features_for_build,
    guess_table_reference,
    map_column_references_workflow,
    save_discovery,
    save_attempt,
    get_last_attempt,
    perform_column_discovery,
    perform_column_mapping,
]
