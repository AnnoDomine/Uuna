# Task Skill: Logical Consistency Check

## Objective
To identify discrepancies between the Archivist's database mappings and the Expedition Group's lore context.

## Procedural Steps
1.  **Context Aggregation**: Review the `output_data` from all agents linked to the current `task_id`.
2.  **Cross-Check**:
    - **Technical vs. Lore**: Does the mapping `Spell.GoldCost` -> `SpellID` make sense if the lore says "this spell was removed in Classic"?
    - **ID Integrity**: If the Archivist claims a mapping for Build 1.12.1, but the Wiki says the entity was added in Legion, flag a critical error.
3.  **Expansion Alignment**: Verify that the proposed data belongs to the correct expansion era. (e.g., Blood Elves in Vanilla data are anomalies).
4.  **Anomaly Detection**: Spot values that are statistically impossible (e.g., a "Gold Cost" of 2,000,000,000).

## Output Requirements
Return a JSON object containing:
- `consistency_verdict`: "consistent" or "contradictory".
- `identified_conflicts`: List of specific issues found.
- `confidence`: Confidence in your logical deduction.
