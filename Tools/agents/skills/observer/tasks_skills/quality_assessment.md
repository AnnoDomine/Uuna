# Task Skill: Quality Assessment

## Objective
To provide a ruthless evaluation of an agent's output based on accuracy, formatting, and strict adherence to protocol.

## Procedural Steps
1.  **Analyze Context**: Use `get_task_context` to identify all finalized events.
2.  **Logic Audit**: Audit reasoning steps in `event_logs`.
3.  **Execute Scoring**: Run the scoring AI for each event.
4.  **Final Relay**:
    - Pass the `task_id` back to the **Courier**.

## Output Requirements
Return a JSON object containing:
- `task_id`: The ID of the task you evaluated.
- `next_agent`: "Courier"
- `status`: "Scores finalized."
