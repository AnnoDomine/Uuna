# Task Skill: Column Discovery

## Objective
To determine the semantic meaning and functional role of a specific database column within a WoW DB2 table.

## Procedural Steps
1.  **Analyze Assignment**: Use `get_event_data` to understand the target table and column assigned by the Courier.
2.  **Analyze Samples**: Examine at least 10 data samples to identify patterns.
3.  **Statistcial Review**: Check min/max values and distinct ratios.
4.  **Semantic Guessing**:
    - Endings in `ID`: Reference candidate.
    - Endings in `msec`: Time durations.
5.  **Final Relay**:
    - Call `create_task_event` with `target="Courier"` and the discovery results as `input_data`.
    - Return the newly generated `event_id`.

## Output Requirements
Return a JSON object containing:
- `event_id`: The ID of the event created for the Courier.
- `target`: "Courier"
- `confidence`: Numeric value.
