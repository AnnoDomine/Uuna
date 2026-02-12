# Task Skill: Complexity Assessment

## Objective
To quantify the difficulty of a research request to set appropriate performance expectations.

## Procedural Steps
1.  **Analyze Query**: Break down the Librarian's request into its components (e.g., Table Name, Column Name, Lore Target).
2.  **Factor Identification**:
    - **Depth**: How many tables must be joined?
    - **History**: Is a multi-build comparison required?
    - **Ambiguity**: Is the column name already semantically clear (e.g., `QuestID`) or cryptic (e.g., `Field_735`)?
3.  **Tier Assignment**:
    - **Tier 1 (Simple)**: Direct ID lookup or simple value extraction.
    - **Tier 2 (Moderate)**: Mapping a single foreign key with statistical proof.
    - **Tier 3 (Complex)**: Multi-step lore discovery or mapping highly ambiguous columns.

## Output Requirements
Return a JSON object containing:
- `complexity_tier`: 1, 2, or 3.
- `difficulty_factors`: List of reasons for the tier choice.
