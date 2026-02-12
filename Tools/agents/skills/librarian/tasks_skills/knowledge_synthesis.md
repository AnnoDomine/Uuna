# Task Skill: Knowledge Synthesis

## Objective
To merge technical data points and lore research into a unified, human-readable answer.

## Procedural Steps
1.  **Analyze Finalized Task**: You receive a `task_id` from the Courier marked as finalized.
2.  **Collect Evidence**: Use `get_verified_results` to gather all finalized findings.
3.  **Construct Response**:
    - **Context**: State the build version(s).
    - **Technical Fact**: Database links.
    - **Lore Context**: Historical background.
4.  **Translation**: Translate into the language defined by the `localisation` setting for the user.

## Output Requirements
Return a JSON object containing:
- `response_local`: The final user-facing text in the requested language.
- `certainty_score`: Average confidence of the contributing agents.
- `references`: List of table rows and Wiki URLs used.
