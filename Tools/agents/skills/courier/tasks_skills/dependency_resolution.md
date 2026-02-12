# Task Skill: Dependency Resolution

## Objective
To ensure all prerequisites (data, indexing, previous results) are met before assigning a task to a high-resource agent.

## Procedural Steps
1.  **Build Verification**: Call `check_build_status` to ensure the targeted WoW version is downloaded and indexed.
2.  **Prerequisite Check**:
    - For **Archivist**: Does the table exist in the DuckDB Master?
    - For **Expedition Group**: Is internet access enabled for the current run?
    - For **Sages**: Are there at least two verified findings from other specialists?
3.  **Conflict Detection**: Check if another task is already modifying the same `global_knowledge` entry.
4.  **Halt & Notify**: If a dependency is missing, change task status to `stalled` and notify the **Librarian**.

## Output Requirements
Return a JSON object containing:
- `dependencies_met`: Boolean.
- `missing_items`: List of strings.
- `recommended_action`: e.g., "Wait for indexing", "Trigger Admin sync".
