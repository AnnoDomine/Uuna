# Task Skill: Knowledge Synthesis

## Objective
To merge technical data points and lore research into a unified, human-readable answer.

## Procedural Steps
1.  **Collect Evidence**: Gather the `output_data` from all finalized events related to the query.
2.  **Verify Status**: Ensure the **Sages** have granted an `APPROVE` verdict.
3.  **Construct Response**:
    - **Context**: State the build version(s) the information is based on.
    - **Technical Fact**: e.g., "In the database, Spell X is linked to NPC Y via field Z."
    - **Lore Context**: e.g., "This NPC represents the leader of the Kirin Tor during the Wrath of the Lich King expansion."
4.  **Translation**: Translate the final synthesis into **German** for the user.

## Output Requirements
Return a JSON object containing:
- `response_german`: The final user-facing text.
- `certainty_score`: Average confidence of the contributing agents.
- `references`: List of table rows and Wiki URLs used.
