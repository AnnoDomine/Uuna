# Task Skill: Column Mapping

## Objective
To identify the correct target table for a foreign key column and provide empirical proof of the relationship.

## Procedural Steps
1.  **Analyze Discovery**: Use `get_event_data` to read the preceding discovery results.
2.  **Statistical Prediction**: Query `research.statistical_predictions` to see if automated analysis has already found ID overlaps.
3.  **Empirical Proof (ID Check)**: Execute a `check_ids` operation. A mapping is only valid if a significant percentage of samples exist in the target table's primary keys.
4.  **Final Relay**:
    - Call `create_task_event` with `target="Courier"` and the mapping data as `input_data`.
    - Return the newly generated `event_id`.

## Output Requirements
Return a JSON object containing:
- `event_id`: The ID of the event created for the Courier.
- `target_role`: "Courier"
- `confidence`: Based on the ID check success rate.
- `reasoning`: Why this table is the correct match.
