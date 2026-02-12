# Task Skill: Potential Score Assignment

## Objective
To assign a `Max_Potential` integer value to a task, defining the performance ceiling.

## Procedural Steps
1.  **Analyze Events**: Use `get_task_context` to identify all events that require scoring.
2.  **Base Potential**:
    - Tier 1: 50 points.
    - Tier 2: 100 points.
    - Tier 3: 200 points.
3.  **Finalize Baseline**: Write the values to the DB using `assign_potential_score`.
4.  **Handover**: Pass the `task_id` to the **Observer**.

## Output Requirements
Return a JSON object containing:
- `task_id`: The ID of the task you processed.
- `next_agent`: "Observer"
- `status`: "Potentials assigned."
