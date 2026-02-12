# Task Skill: Task Routing

## Objective
To determine the most efficient next step for a research task based on its current status and the available agent pool.

## Procedural Steps
1.  **Analyze Input**: Read the initial user query and the current `task_id` context.
2.  **Evaluate Progress**:
    - If the task is brand new: Route to **Librarian** or **Archivist** for initial assessment.
    - If IDs are missing: Route to **Archivist**.
    - If lore context is missing: Route to **Expedition Group**.
    - If technical mapping is proposed: Route to **The Sages** for verification.
    - If all data is gathered and APPROVED by Sages: Route to **Tinker** to start the scoring relay.
    - If scoring is finished: Route to **Librarian** for final answer synthesis.
3.  **Check Confidence**: If the previous agent's output has a confidence `< 0.7`, do not advance the task. Instead, route back to **Research** or flag for **Admin** intervention.
4.  **Assign Agent**: Update the `current_location` field in the `research.tasks` table and spawn a new `task_event`.

## Constraints
- **Isolation**: Agents must never talk directly to each other. You are the only link.
- **Auditability**: Every routing decision must be logged with a reason in the `event_logs`.

## Output Requirements
Return a JSON object containing:
- `next_agent`: The role name of the specialist.
- `priority`: Integer (1-5).
- `reasoning`: Detailed explanation of why this agent was chosen.
