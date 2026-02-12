# Task Skill: Structural Context Search

## Objective
To obtain community-defined schema information and headers for WoW DB2 tables to aid the Archivist's mapping process.

## Procedural Steps
1.  **Analyze Assignment**: Use `get_event_data` to identify the table and build assigned by the Courier.
2.  **Header Retrieval**: Call `get_wago_structure` for the specific table and build version.
3.  **Relay to Sentinel**:
    - Call `create_task_event` with `target="Sentinel"` and the structure data as `input_data`.
    - Provide the newly created `event_id` as your final output.

## Output Requirements
Return a JSON object containing:
- `event_id`: The ID of the event created for the Sentinel.
- `target`: "Sentinel"
- `confidence`: High if exact build match found.
