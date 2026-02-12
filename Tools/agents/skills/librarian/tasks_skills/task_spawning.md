# Task Skill: Task Spawning

## Objective
To initiate a formal research process in the system when existing knowledge is missing.

## Procedural Steps
1.  **Check Build**: Run `check_build_status` for the target version.
2.  **Define Objective**: Write a clear, English-language research query (e.g., "Identify the relationship between GuldansSpellID and the Boss encounter table").
3.  **Create Record**: Insert a new row into `research.tasks` with status `spawned`.
4.  **Handover**: Notify the **Courier** by passing the `task_id`.

## Output Requirements
Return a JSON object containing:
- `task_id`: Newly generated UUID.
- `assigned_agent`: Always `Courier`.
- `initial_status`: `spawned`.
