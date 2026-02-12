# Task Skill: Final Verdict Approval

## Objective
To provide the definitive decision on whether a research task is complete and accurate enough to be archived.

## Procedural Steps
1.  **Analyze Context**: Use `get_task_context` to verify technical proof and lore context are complete.
2.  **Review Observer Score**: Note any quality warnings.
3.  **Final Relay**:
    - Call `create_task_event` with `target="Courier"` and the verdict data as `input_data`.
    - Return the newly generated `event_id`.

## Output Requirements
Return a JSON object containing:
- `event_id`: The ID of the event created for the Courier.
- `target`: "Courier"
- `decision`: "APPROVE" or "BLOCK".
- `reasoning`: The final justification.
