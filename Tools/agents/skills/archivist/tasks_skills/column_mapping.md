# Task Skill: Column Mapping

## Objective
To identify the correct target table for a foreign key column and provide empirical proof of the relationship.

## Procedural Steps
1.  **Identity Target Candidate**: Based on the `Column Discovery` result and the column name (e.g., `SpellID` -> `Spell`), select potential target tables.
2.  **Statistical Prediction**: Query `research.statistical_predictions` to see if automated analysis has already found ID overlaps.
3.  **Cross-Check Consistency**: Ensure that if similar columns exist in the table (e.g., `QuestID_1`, `QuestID_2`), they point to the same target.
4.  **Empirical Proof (ID Check)**: Execute a `check_ids` operation. A mapping is only valid if a significant percentage of samples exist in the target table's primary keys.
5.  **Sages Review**: Present the findings, including the "Proof" (match count), to The Sages for final logic verification and approval.

## Constraints
- **Absolute Match**: If the target table is missing in the current build, the mapping must be flagged as "Pending".
- **Naming Accuracy**: Use the exact table names as found in the registry.

## Output Requirements
Return a JSON object containing:
- `target`: The confirmed table name.
- `confidence`: Based on the ID check success rate.
- `reasoning`: Why this table is the correct match.
